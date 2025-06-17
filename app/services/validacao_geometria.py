import zipfile
import io
import os
import uuid
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import datetime
import tempfile
import geopandas as gpd
import pandas as pd

class ValidadorZipShapefile:
    """Valida arquivos ZIP contendo shapefiles"""
    
    ARQUIVOS_OBRIGATORIOS = ['.shp', '.shx', '.dbf', '.prj']
    ARQUIVOS_OPCIONAIS = ['.cpg', '.sbn', '.sbx', '.xml']
    TAMANHO_MAX_ZIP = 50 * 1024 * 1024  # 50MB
    
    def __init__(self, db: Session):
        self.db = db
        self.erros = []
        self.warnings = []
        
    def validar_zip(self, arquivo_zip: bytes, nome_arquivo: str) -> Dict[str, Any]:
        """Valida o arquivo ZIP e retorna resultado da validação"""
        
        projeto_temp_id = str(uuid.uuid4())
        
        try:
            # Teste 1: Tamanho do arquivo
            if len(arquivo_zip) > self.TAMANHO_MAX_ZIP:
                self.erros.append(f"Arquivo muito grande: {len(arquivo_zip)/1024/1024:.1f}MB. Máximo permitido: 50MB")
            
            # Teste 2: Formato ZIP válido
            try:
                with zipfile.ZipFile(io.BytesIO(arquivo_zip), 'r') as zip_ref:
                    arquivos = zip_ref.namelist()
            except zipfile.BadZipFile:
                self.erros.append("Arquivo não é um ZIP válido")
                return self._gerar_resultado_erro(projeto_temp_id, nome_arquivo)
            
            # Teste 3: Verificar arquivos obrigatórios
            extensoes_encontradas = [os.path.splitext(arq)[1].lower() for arq in arquivos]
            
            for ext_obrigatoria in self.ARQUIVOS_OBRIGATORIOS:
                if ext_obrigatoria not in extensoes_encontradas:
                    self.erros.append(f"Arquivo obrigatório não encontrado: *{ext_obrigatoria}")
            
            # Teste 4: Verificar se há arquivos extras desnecessários
            extensoes_validas = self.ARQUIVOS_OBRIGATORIOS + self.ARQUIVOS_OPCIONAIS
            for arquivo in arquivos:
                ext = os.path.splitext(arquivo)[1].lower()
                if ext and ext not in extensoes_validas:
                    self.warnings.append(f"Arquivo não padrão encontrado: {arquivo}")
            
            # Se há erros críticos, interrompe o fluxo
            if self.erros:
                return self._gerar_resultado_erro(projeto_temp_id, nome_arquivo)
            
            # Teste 5: Extrair e validar conteúdo dos arquivos
            resultado_extracao = self._extrair_e_validar_arquivos(arquivo_zip, projeto_temp_id)
            
            if resultado_extracao['status'] == 'erro':
                return resultado_extracao
            
            return {
                'status': 'sucesso',
                'projeto_temp_id': projeto_temp_id,
                'mensagem': 'ZIP validado com sucesso!',
                'warnings': self.warnings,
                'proximo_passo': 'validar_geometria'
            }
            
        except Exception as e:
            self.erros.append(f"Erro inesperado na validação: {str(e)}")
            return self._gerar_resultado_erro(projeto_temp_id, nome_arquivo)
    
    def _extrair_e_validar_arquivos(self, arquivo_zip: bytes, projeto_temp_id: str) -> Dict[str, Any]:
        """Extrai arquivos do ZIP e salva na tabela temporária"""
        
        from app.models.pr_projeto_geometria import GeometriaValidacaoTemporaria
        
        try:
            dados_arquivos = {}
            
            with zipfile.ZipFile(io.BytesIO(arquivo_zip), 'r') as zip_ref:
                for arquivo in zip_ref.namelist():
                    ext = os.path.splitext(arquivo)[1].lower()
                    if ext in self.ARQUIVOS_OBRIGATORIOS:
                        dados_arquivos[ext] = zip_ref.read(arquivo)
            
            # Salvar na tabela temporária
            geometria_temp = GeometriaValidacaoTemporaria(
                projeto_temp_id=projeto_temp_id,
                arquivo_original=projeto_temp_id + '.zip',
                dados_shp=dados_arquivos.get('.shp'),
                dados_shx=dados_arquivos.get('.shx'),
                dados_dbf=dados_arquivos.get('.dbf'),
                dados_prj=dados_arquivos.get('.prj'),
                status_validacao='extraido'
            )
            
            self.db.add(geometria_temp)
            self.db.commit()
            
            return {
                'status': 'sucesso',
                'projeto_temp_id': projeto_temp_id,
                'dados_extraidos': True
            }
            
        except Exception as e:
            self.erros.append(f"Erro ao extrair arquivos: {str(e)}")
            return self._gerar_resultado_erro(projeto_temp_id, '')
    
    def _gerar_resultado_erro(self, projeto_temp_id: str, nome_arquivo: str) -> Dict[str, Any]:
        """Gera resultado de erro e PDF de relatório"""
        
        # Gerar PDF de erro
        pdf_path = self._gerar_pdf_erro(projeto_temp_id, nome_arquivo)
        
        return {
            'status': 'erro',
            'projeto_temp_id': projeto_temp_id,
            'erros': self.erros,
            'warnings': self.warnings,
            'pdf_erro_path': pdf_path,
            'mensagem': f'Validação falhou. {len(self.erros)} erro(s) encontrado(s).',
            'fluxo_interrompido': True
        }
    
    def _gerar_pdf_erro(self, projeto_temp_id: str, nome_arquivo: str) -> str:
        """Gera PDF com relatório de erros detalhado"""
        
        # Criar diretório se não existir
        relatorio_dir = f"app/static/relatorios/validacao"
        os.makedirs(relatorio_dir, exist_ok=True)
        
        pdf_filename = f"erro_validacao_{projeto_temp_id}.pdf"
        pdf_path = os.path.join(relatorio_dir, pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.red
        )
        story.append(Paragraph("RELATÓRIO DE VALIDAÇÃO - ERRO", title_style))
        story.append(Spacer(1, 12))
        
        # Informações gerais
        info_data = [
            ['Arquivo:', nome_arquivo],
            ['ID Temporário:', projeto_temp_id],
            ['Data/Hora:', datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
            ['Status:', 'ERRO NA VALIDAÇÃO']
        ]
        
        info_table = Table(info_data, colWidths=[100, 300])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Erros encontrados
        story.append(Paragraph("ERROS ENCONTRADOS:", styles['Heading2']))
        for i, erro in enumerate(self.erros, 1):
            story.append(Paragraph(f"{i}. {erro}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Como corrigir
        story.append(Paragraph("COMO CORRIGIR:", styles['Heading2']))
        correcoes = [
            "1. Verifique se o arquivo é um ZIP válido",
            "2. Certifique-se de que contenha: .shp, .shx, .dbf, .prj",
            "3. Tamanho máximo permitido: 50MB",
            "4. Use apenas arquivos de shapefile padrão",
            "5. Comprima os arquivos em um único ZIP"
        ]
        
        for correcao in correcoes:
            story.append(Paragraph(correcao, styles['Normal']))
        
        doc.build(story)
        
        return f"/static/relatorios/validacao/{pdf_filename}"


class ValidadorGeometria:
    """Valida a geometria do shapefile extraído"""
    
    def __init__(self, db: Session):
        self.db = db
        self.erros = []
        self.warnings = []
    
    def validar_geometria(self, projeto_temp_id: str) -> Dict[str, Any]:
        """Valida a geometria extraída"""
        
        from app.models.pr_projeto_geometria import GeometriaValidacaoTemporaria, GeometriaValidada
        
        try:
            # Recuperar dados da tabela temporária
            geom_temp = self.db.query(GeometriaValidacaoTemporaria).filter(
                GeometriaValidacaoTemporaria.projeto_temp_id == projeto_temp_id
            ).first()
            
            if not geom_temp:
                return self._gerar_resultado_erro(projeto_temp_id, "Dados temporários não encontrados")
            
            # Criar arquivos temporários para processar com geopandas
            resultado_processamento = self._processar_com_geopandas(geom_temp)
            
            if resultado_processamento['status'] == 'erro':
                return resultado_processamento
            
            # Salvar geometria validada
            geometria_validada = GeometriaValidada(
                projeto_temp_id=projeto_temp_id,
                geom_wkt=resultado_processamento['wkt'],
                srid=resultado_processamento['srid'],
                area_m2=resultado_processamento.get('area_m2'),
                perimetro_m=resultado_processamento.get('perimetro_m'),
                centroide_lat=resultado_processamento.get('centroide_lat'),
                centroide_lon=resultado_processamento.get('centroide_lon'),
                bbox_min_x=resultado_processamento.get('bbox_min_x'),
                bbox_min_y=resultado_processamento.get('bbox_min_y'),
                bbox_max_x=resultado_processamento.get('bbox_max_x'),
                bbox_max_y=resultado_processamento.get('bbox_max_y')
            )
            
            self.db.add(geometria_validada)
            
            # Atualizar status da tabela temporária
            geom_temp.status_validacao = 'validado'
            self.db.commit()
            
            # Gerar PDF de sucesso
            pdf_path = self._gerar_pdf_sucesso(projeto_temp_id, resultado_processamento)
            
            return {
                'status': 'sucesso',
                'projeto_temp_id': projeto_temp_id,
                'mensagem': 'Geometria validada com sucesso!',
                'geometria_dados': resultado_processamento,
                'pdf_sucesso_path': pdf_path,
                'proximo_passo': 'visualizar_mapa'
            }
            
        except Exception as e:
            return self._gerar_resultado_erro(projeto_temp_id, f"Erro na validação: {str(e)}")
    
    def _processar_com_geopandas(self, geom_temp) -> Dict[str, Any]:
        """Processa shapefile com geopandas"""
        
        try:
            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                # Salvar arquivos temporários
                shp_path = os.path.join(temp_dir, "temp.shp")
                shx_path = os.path.join(temp_dir, "temp.shx")
                dbf_path = os.path.join(temp_dir, "temp.dbf")
                prj_path = os.path.join(temp_dir, "temp.prj")
                
                with open(shp_path, 'wb') as f:
                    f.write(geom_temp.dados_shp)
                with open(shx_path, 'wb') as f:
                    f.write(geom_temp.dados_shx)
                with open(dbf_path, 'wb') as f:
                    f.write(geom_temp.dados_dbf)
                with open(prj_path, 'wb') as f:
                    f.write(geom_temp.dados_prj)
                
                # Ler com geopandas
                gdf = gpd.read_file(shp_path)
                
                # Validações geométricas
                if gdf.empty:
                    self.erros.append("Shapefile não contém geometrias")
                    return {'status': 'erro'}
                
                if len(gdf) > 1:
                    self.warnings.append(f"Shapefile contém {len(gdf)} feições. Apenas a primeira será usada.")
                
                # Pegar primeira geometria
                geom = gdf.geometry.iloc[0]
                
                # Validar geometria
                if not geom.is_valid:
                    self.erros.append("Geometria inválida encontrada")
                    return {'status': 'erro'}
                
                # Reprojetar para WGS84 se necessário
                if gdf.crs != 'EPSG:4326':
                    gdf = gdf.to_crs('EPSG:4326')
                    geom = gdf.geometry.iloc[0]
                
                # Calcular propriedades
                bounds = geom.bounds
                centroide = geom.centroid
                
                resultado = {
                    'status': 'sucesso',
                    'wkt': geom.wkt,
                    'srid': 4326,
                    'centroide_lat': centroide.y,
                    'centroide_lon': centroide.x,
                    'bbox_min_x': bounds[0],
                    'bbox_min_y': bounds[1],
                    'bbox_max_x': bounds[2],
                    'bbox_max_y': bounds[3],
                    'tipo_geometria': geom.geom_type,
                    'num_vertices': len(geom.coords) if hasattr(geom, 'coords') else 'N/A'
                }
                
                # Calcular área e perímetro se for polígono
                if geom.geom_type in ['Polygon', 'MultiPolygon']:
                    # Reprojetar para UTM para cálculos métricos
                    gdf_utm = gdf.to_crs('EPSG:3857')  # Web Mercator para aproximação
                    geom_utm = gdf_utm.geometry.iloc[0]
                    resultado['area_m2'] = geom_utm.area
                    resultado['perimetro_m'] = geom_utm.length
                
                return resultado
                
        except Exception as e:
            self.erros.append(f"Erro no processamento: {str(e)}")
            return {'status': 'erro'}
    
    def _gerar_resultado_erro(self, projeto_temp_id: str, mensagem_adicional: str) -> Dict[str, Any]:
        """Gera resultado de erro para geometria"""
        
        # Gerar PDF de erro
        pdf_path = self._gerar_pdf_erro_geometria(projeto_temp_id, mensagem_adicional)
        
        return {
            'status': 'erro',
            'projeto_temp_id': projeto_temp_id,
            'erros': self.erros,
            'warnings': self.warnings,
            'pdf_erro_path': pdf_path,
            'mensagem': f'Validação de geometria falhou: {mensagem_adicional}',
            'fluxo_interrompido': True
        }
    
    def _gerar_pdf_erro_geometria(self, projeto_temp_id: str, mensagem: str) -> str:
        """Gera PDF de erro para validação de geometria"""
        
        relatorio_dir = f"app/static/relatorios/geometria"
        os.makedirs(relatorio_dir, exist_ok=True)
        
        pdf_filename = f"erro_geometria_{projeto_temp_id}.pdf"
        pdf_path = os.path.join(relatorio_dir, pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.red
        )
        story.append(Paragraph("RELATÓRIO DE VALIDAÇÃO DE GEOMETRIA - ERRO", title_style))
        story.append(Spacer(1, 12))
        
        # Informações
        story.append(Paragraph(f"ID Temporário: {projeto_temp_id}", styles['Normal']))
        story.append(Paragraph(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Erro: {mensagem}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Erros detalhados
        if self.erros:
            story.append(Paragraph("ERROS ENCONTRADOS:", styles['Heading2']))
            for erro in self.erros:
                story.append(Paragraph(f"• {erro}", styles['Normal']))
        
        doc.build(story)
        return f"/static/relatorios/geometria/{pdf_filename}"
    
    def _gerar_pdf_sucesso(self, projeto_temp_id: str, dados_geometria: Dict) -> str:
        """Gera PDF de sucesso com dados da geometria"""
        
        relatorio_dir = f"app/static/relatorios/geometria"
        os.makedirs(relatorio_dir, exist_ok=True)
        
        pdf_filename = f"sucesso_geometria_{projeto_temp_id}.pdf"
        pdf_path = os.path.join(relatorio_dir, pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.green
        )
        story.append(Paragraph("RELATÓRIO DE VALIDAÇÃO DE GEOMETRIA - SUCESSO", title_style))
        story.append(Spacer(1, 12))
        
        # Dados da geometria
        info_data = [
            ['ID Temporário:', projeto_temp_id],
            ['Data/Hora:', datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
            ['Status:', 'GEOMETRIA VALIDADA'],
            ['Tipo:', dados_geometria.get('tipo_geometria', 'N/A')],
            ['SRID:', dados_geometria.get('srid', 'N/A')],
            ['Centroide (Lat):', f"{dados_geometria.get('centroide_lat', 0):.6f}"],
            ['Centroide (Lon):', f"{dados_geometria.get('centroide_lon', 0):.6f}"],
        ]
        
        if dados_geometria.get('area_m2'):
            info_data.append(['Área (m²):', f"{dados_geometria['area_m2']:.2f}"])
        if dados_geometria.get('perimetro_m'):
            info_data.append(['Perímetro (m):', f"{dados_geometria['perimetro_m']:.2f}"])
        
        info_table = Table(info_data, colWidths=[120, 300])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        
        doc.build(story)
        return f"/static/relatorios/geometria/{pdf_filename}"
