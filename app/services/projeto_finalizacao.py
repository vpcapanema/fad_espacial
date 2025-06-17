import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import base64
from io import BytesIO
from PIL import Image as PILImage

class GeradorCroqui:
    """Gera croqui baseado no estado atual do mapa Leaflet"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def gerar_croqui(self, projeto_temp_id: str, dados_mapa: Dict[str, Any]) -> Dict[str, Any]:
        """
        ETAPA 4: Gera croqui fiel ao mapa Leaflet
        
        Parâmetros:
        - projeto_temp_id: ID temporário do projeto
        - dados_mapa: {
            'basemap_selecionado': 'osm|sat|opaco',
            'zoom': int,
            'centro': {'lat': float, 'lon': float},
            'imagem_base64': 'string'  # Screenshot do mapa
          }
        """
        try:
            # Validar dados de entrada
            if not dados_mapa.get('imagem_base64'):
                return {
                    'status': 'erro',
                    'mensagem': 'Imagem do mapa não fornecida'
                }
            
            # Criar diretório do projeto
            projeto_dir = f"app/static/projetos/{projeto_temp_id}"
            os.makedirs(projeto_dir, exist_ok=True)
            
            # Salvar imagem do croqui
            caminho_croqui = self._salvar_imagem_croqui(
                projeto_temp_id, 
                dados_mapa['imagem_base64'],
                projeto_dir
            )
            
            # Gerar metadados do croqui
            metadados = {
                'projeto_temp_id': projeto_temp_id,
                'basemap_selecionado': dados_mapa.get('basemap_selecionado', 'osm'),
                'zoom': dados_mapa.get('zoom', 10),
                'centro': dados_mapa.get('centro', {}),
                'gerado_em': datetime.now().isoformat(),
                'caminho_imagem': caminho_croqui
            }
            
            # Salvar metadados
            metadados_path = os.path.join(projeto_dir, 'croqui_metadados.json')
            with open(metadados_path, 'w') as f:
                json.dump(metadados, f, indent=2)
            
            return {
                'status': 'sucesso',
                'caminho_croqui': caminho_croqui,
                'metadados': metadados,
                'mensagem': 'Croqui gerado com sucesso!'
            }
            
        except Exception as e:
            return {
                'status': 'erro',
                'mensagem': f'Erro ao gerar croqui: {str(e)}'
            }
    
    def _salvar_imagem_croqui(self, projeto_temp_id: str, imagem_base64: str, projeto_dir: str) -> str:
        """Salva a imagem do croqui a partir do base64"""
        
        try:
            # Remover prefixo data:image/png;base64, se existir
            if ',' in imagem_base64:
                imagem_base64 = imagem_base64.split(',')[1]
            
            # Decodificar base64
            image_data = base64.b64decode(imagem_base64)
            
            # Abrir com PIL para processamento
            image = PILImage.open(BytesIO(image_data))
            
            # Salvar como PNG de alta qualidade
            filename = f"croqui_{projeto_temp_id}.png"
            caminho_completo = os.path.join(projeto_dir, filename)
            image.save(caminho_completo, 'PNG', quality=95)
            
            # Retornar caminho relativo para web
            return f"/static/projetos/{projeto_temp_id}/{filename}"
            
        except Exception as e:
            raise Exception(f"Erro ao salvar imagem: {str(e)}")


class FinalizadorProjeto:
    """Finaliza o projeto e gera todos os relatórios"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def finalizar_projeto(self, dados_finalizacao: Dict[str, Any]) -> Dict[str, Any]:
        """
        ETAPA 5: Finaliza projeto e gera relatórios completos
        
        Parâmetros:
        - projeto_temp_id: ID temporário
        - dados_projeto: Dados do formulário
        - caminho_croqui: Caminho do croqui gerado
        """
        try:
            projeto_temp_id = dados_finalizacao['projeto_temp_id']
            
            # Gerar código único do projeto
            codigo_projeto = self._gerar_codigo_projeto()
            
            # Criar estrutura de diretórios
            projeto_dir = f"app/static/projetos/{projeto_temp_id}"
            os.makedirs(projeto_dir, exist_ok=True)
            
            # Salvar dados no banco
            resultado_bd = self._salvar_projeto_banco(dados_finalizacao, codigo_projeto)
            
            if resultado_bd['status'] == 'erro':
                return resultado_bd
            
            # Gerar JSON do projeto
            json_path = self._gerar_json_projeto(dados_finalizacao, codigo_projeto, projeto_dir)
            
            # Gerar PDF completo
            pdf_path = self._gerar_pdf_completo(dados_finalizacao, codigo_projeto, projeto_dir)
            
            # Atualizar registro no banco com caminhos dos arquivos
            self._atualizar_caminhos_arquivos(resultado_bd['projeto_id'], json_path, pdf_path)
            
            return {
                'status': 'sucesso',
                'codigo_projeto': codigo_projeto,
                'projeto_id': resultado_bd['projeto_id'],
                'pdf_relatorio_completo': pdf_path,
                'json_projeto': json_path,
                'mensagem': f'Projeto {codigo_projeto} finalizado com sucesso!'
            }
            
        except Exception as e:
            return {
                'status': 'erro',
                'mensagem': f'Erro ao finalizar projeto: {str(e)}'
            }
    
    def _gerar_codigo_projeto(self) -> str:
        """Gera código único para o projeto"""
        ano = datetime.now().year
        timestamp = datetime.now().strftime("%m%d%H%M")
        return f"PROJ-{ano}-{timestamp}"
    
    def _salvar_projeto_banco(self, dados: Dict[str, Any], codigo_projeto: str) -> Dict[str, Any]:
        """Salva projeto finalizado no banco de dados"""
        
        try:
            from app.models.pr_projeto_geometria import ProjetoFinalizado, GeometriaValidada
            
            # Buscar geometria validada
            geometria = self.db.query(GeometriaValidada).filter(
                GeometriaValidada.projeto_temp_id == dados['projeto_temp_id']
            ).first()
            
            if not geometria:
                return {
                    'status': 'erro',
                    'mensagem': 'Geometria validada não encontrada'
                }
            
            # Criar registro do projeto
            projeto = ProjetoFinalizado(
                codigo_projeto=codigo_projeto,
                tipo_projeto=dados['tipo_projeto'],
                interessado_id=dados['interessado_id'],
                representante_id=dados['representante_id'],
                tipo_elemento_rodoviario=dados['tipo_elemento_rodoviario'],
                elemento_rodoviario_id=dados['elemento_rodoviario_id'],
                geometria_validada_id=geometria.id,
                caminho_croqui=dados['caminho_croqui'],
                basemap_selecionado=dados.get('basemap_selecionado', 'osm'),
                zoom_croqui=dados.get('zoom_croqui', 10),
                json_projeto_path='',  # Será atualizado depois
                pdf_relatorio_path='',  # Será atualizado depois
                status='finalizado'
            )
            
            self.db.add(projeto)
            self.db.commit()
            self.db.refresh(projeto)
            
            return {
                'status': 'sucesso',
                'projeto_id': projeto.id
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                'status': 'erro',
                'mensagem': f'Erro ao salvar no banco: {str(e)}'
            }
    
    def _gerar_json_projeto(self, dados: Dict[str, Any], codigo_projeto: str, projeto_dir: str) -> str:
        """Gera JSON completo do projeto para análises futuras"""
        
        from app.models.pr_projeto_geometria import GeometriaValidada
        
        # Buscar dados completos da geometria
        geometria = self.db.query(GeometriaValidada).filter(
            GeometriaValidada.projeto_temp_id == dados['projeto_temp_id']
        ).first()
        
        # Estruturar dados completos
        projeto_json = {
            'metadados': {
                'codigo_projeto': codigo_projeto,
                'versao_sistema': '1.0',
                'gerado_em': datetime.now().isoformat(),
                'usuario_responsavel': dados.get('usuario_id', 'sistema')
            },
            'dados_projeto': {
                'tipo_projeto': dados['tipo_projeto'],
                'interessado_id': dados['interessado_id'],
                'representante_id': dados['representante_id'],
                'tipo_elemento_rodoviario': dados['tipo_elemento_rodoviario'],
                'elemento_rodoviario_id': dados['elemento_rodoviario_id']
            },
            'geometria': {
                'wkt': geometria.geom_wkt if geometria else None,
                'srid': geometria.srid if geometria else None,
                'area_m2': geometria.area_m2 if geometria else None,
                'perimetro_m': geometria.perimetro_m if geometria else None,
                'centroide': {
                    'lat': geometria.centroide_lat if geometria else None,
                    'lon': geometria.centroide_lon if geometria else None
                },
                'bbox': {
                    'min_x': geometria.bbox_min_x if geometria else None,
                    'min_y': geometria.bbox_min_y if geometria else None,
                    'max_x': geometria.bbox_max_x if geometria else None,
                    'max_y': geometria.bbox_max_y if geometria else None
                }
            },
            'croqui': {
                'caminho_arquivo': dados['caminho_croqui'],
                'basemap_utilizado': dados.get('basemap_selecionado', 'osm'),
                'zoom_nivel': dados.get('zoom_croqui', 10)
            },
            'processamento': {
                'projeto_temp_id': dados['projeto_temp_id'],
                'etapas_concluidas': [
                    'validacao_zip',
                    'validacao_geometria',
                    'visualizacao_mapa',
                    'geracao_croqui',
                    'finalizacao_projeto'
                ]
            }
        }
        
        # Salvar JSON
        json_filename = f"projeto_{codigo_projeto}.json"
        json_path = os.path.join(projeto_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(projeto_json, f, indent=2, ensure_ascii=False)
        
        return f"/static/projetos/{dados['projeto_temp_id']}/{json_filename}"
    
    def _gerar_pdf_completo(self, dados: Dict[str, Any], codigo_projeto: str, projeto_dir: str) -> str:
        """Gera PDF completo com relatório de todas as etapas"""
        
        pdf_filename = f"relatorio_completo_{codigo_projeto}.pdf"
        pdf_path = os.path.join(projeto_dir, pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título principal
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.navy,
            alignment=1  # Centralizado
        )
        story.append(Paragraph("RELATÓRIO COMPLETO DE CADASTRO DE PROJETO", title_style))
        story.append(Spacer(1, 20))
        
        # Informações do projeto
        info_data = [
            ['Código do Projeto:', codigo_projeto],
            ['Data/Hora Finalização:', datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
            ['Tipo de Projeto:', dados.get('tipo_projeto', 'N/A')],
            ['Status:', 'FINALIZADO COM SUCESSO']
        ]
        
        info_table = Table(info_data, colWidths=[130, 300])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Etapas do fluxo
        story.append(Paragraph("ETAPAS CONCLUÍDAS:", styles['Heading2']))
        
        etapas = [
            "✓ ETAPA 1: Preenchimento de dados do projeto",
            "✓ ETAPA 2: Upload e validação do arquivo ZIP",
            "✓ ETAPA 3: Validação da geometria do shapefile",
            "✓ ETAPA 4: Visualização no mapa com malha DER",
            "✓ ETAPA 5: Geração do croqui de localização",
            "✓ ETAPA 6: Finalização e gravação do projeto"
        ]
        
        for etapa in etapas:
            story.append(Paragraph(etapa, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Incluir croqui se disponível
        if dados.get('caminho_croqui'):
            story.append(Paragraph("CROQUI DE LOCALIZAÇÃO:", styles['Heading2']))
            try:
                # Caminho absoluto para o croqui
                croqui_path = dados['caminho_croqui'].replace('/static/', 'app/static/')
                if os.path.exists(croqui_path):
                    img = Image(croqui_path, width=400, height=300)
                    story.append(img)
                else:
                    story.append(Paragraph("Croqui não encontrado no caminho especificado.", styles['Normal']))
            except Exception as e:
                story.append(Paragraph(f"Erro ao incluir croqui: {str(e)}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Arquivos gerados
        story.append(Paragraph("ARQUIVOS GERADOS:", styles['Heading2']))
        arquivos = [
            f"• PDF Relatório Completo: relatorio_completo_{codigo_projeto}.pdf",
            f"• JSON Dados Projeto: projeto_{codigo_projeto}.json",
            f"• Croqui Localização: {os.path.basename(dados.get('caminho_croqui', 'N/A'))}"
        ]
        
        for arquivo in arquivos:
            story.append(Paragraph(arquivo, styles['Normal']))
        
        doc.build(story)
        
        return f"/static/projetos/{dados['projeto_temp_id']}/{pdf_filename}"
    
    def _atualizar_caminhos_arquivos(self, projeto_id: int, json_path: str, pdf_path: str):
        """Atualiza os caminhos dos arquivos no banco de dados"""
        
        from app.models.pr_projeto_geometria import ProjetoFinalizado
        
        projeto = self.db.query(ProjetoFinalizado).filter(
            ProjetoFinalizado.id == projeto_id
        ).first()
        
        if projeto:
            projeto.json_projeto_path = json_path
            projeto.pdf_relatorio_path = pdf_path
            self.db.commit()
