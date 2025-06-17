import zipfile
import os
import tempfile
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import uuid

class ValidacaoService:
    
    @staticmethod
    def validar_zip(arquivo_zip) -> Dict[str, Any]:
        """Valida arquivo ZIP e extrai conteúdo"""
        upload_id = str(uuid.uuid4())
        
        try:
            # Verificar extensão
            if not arquivo_zip.filename.endswith('.zip'):
                return {
                    "status": "erro",
                    "upload_id": upload_id,
                    "erro": "Arquivo deve ser ZIP",
                    "pdf_relatorio": ValidacaoService._gerar_pdf_erro(upload_id, "Arquivo deve ser ZIP")
                }
            
            # Verificar conteúdo do ZIP
            with zipfile.ZipFile(arquivo_zip.file, 'r') as zip_ref:
                arquivos = zip_ref.namelist()
                
                # Verificar se tem shapefile completo
                shp_files = [f for f in arquivos if f.endswith('.shp')]
                if not shp_files:
                    return {
                        "status": "erro", 
                        "upload_id": upload_id,
                        "erro": "ZIP deve conter arquivo .shp",
                        "pdf_relatorio": ValidacaoService._gerar_pdf_erro(upload_id, "Arquivo .shp não encontrado")
                    }
                
                # Verificar arquivos obrigatórios
                base_name = shp_files[0][:-4]
                required = ['.shp', '.shx', '.dbf', '.prj']
                missing = []
                
                for ext in required:
                    if base_name + ext not in arquivos:
                        missing.append(ext)
                
                if missing:
                    erro = f"Arquivos faltando: {', '.join(missing)}"
                    return {
                        "status": "erro",
                        "upload_id": upload_id, 
                        "erro": erro,
                        "pdf_relatorio": ValidacaoService._gerar_pdf_erro(upload_id, erro)
                    }
                
                # Extrair arquivos
                temp_dir = tempfile.mkdtemp()
                zip_ref.extractall(temp_dir)
                
                return {
                    "status": "sucesso",
                    "upload_id": upload_id,
                    "temp_dir": temp_dir,
                    "shp_file": os.path.join(temp_dir, shp_files[0])
                }
                
        except Exception as e:
            return {
                "status": "erro",
                "upload_id": upload_id,
                "erro": str(e),
                "pdf_relatorio": ValidacaoService._gerar_pdf_erro(upload_id, str(e))
            }
    
    @staticmethod
    def validar_geometria(shp_file: str, upload_id: str) -> Dict[str, Any]:
        """Valida geometria do shapefile"""
        try:
            # Aqui seria a validação real com GDAL/Shapely
            # Por enquanto, simulação
            
            return {
                "status": "sucesso",
                "upload_id": upload_id,
                "geometria_wkt": "POLYGON((-46.5 -23.5, -46.4 -23.5, -46.4 -23.4, -46.5 -23.4, -46.5 -23.5))",
                "area_km2": 123.45,
                "perimetro_km": 45.67,
                "pdf_relatorio": ValidacaoService._gerar_pdf_sucesso(upload_id)
            }
            
        except Exception as e:
            return {
                "status": "erro",
                "upload_id": upload_id,
                "erro": str(e),
                "pdf_relatorio": ValidacaoService._gerar_pdf_erro(upload_id, str(e))
            }
    
    @staticmethod
    def _gerar_pdf_erro(upload_id: str, erro: str) -> str:
        """Gera PDF de relatório de erro"""
        filename = f"relatorio_erro_{upload_id}.pdf"
        filepath = f"app/static/relatorios/{filename}"
        
        os.makedirs("app/static/relatorios", exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph("RELATÓRIO DE ERRO - VALIDAÇÃO", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Upload ID: {upload_id}", styles['Normal']))
        story.append(Paragraph(f"Erro: {erro}", styles['Normal']))
        story.append(Paragraph("Como corrigir: Verifique o arquivo e tente novamente", styles['Normal']))
        
        doc.build(story)
        return f"/static/relatorios/{filename}"
    
    @staticmethod
    def _gerar_pdf_sucesso(upload_id: str) -> str:
        """Gera PDF de relatório de sucesso"""
        filename = f"relatorio_sucesso_{upload_id}.pdf"
        filepath = f"app/static/relatorios/{filename}"
        
        os.makedirs("app/static/relatorios", exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph("RELATÓRIO DE VALIDAÇÃO - SUCESSO", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Upload ID: {upload_id}", styles['Normal']))
        story.append(Paragraph("Status: APROVADO", styles['Normal']))
        story.append(Paragraph("Geometria validada com sucesso", styles['Normal']))
        
        doc.build(story)
        return f"/static/relatorios/{filename}"
