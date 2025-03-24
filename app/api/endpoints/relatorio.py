from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.validacao import ValidacaoGeometria
from app.models.arquivos import ArquivoZip
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import geopandas as gpd
import zipfile
import tempfile
import io
import os

router = APIRouter()

@router.get("/relatorio")
def gerar_relatorio_validacao(db: Session = Depends(get_db)):
    try:
        # 🔍 Recupera a última validação
        validacao = db.query(ValidacaoGeometria).order_by(ValidacaoGeometria.id.desc()).first()
        if not validacao:
            raise HTTPException(status_code=404, detail="Nenhuma validação encontrada.")

        # 🔍 Nome do arquivo
        zip_entry = db.query(ArquivoZip).order_by(ArquivoZip.id.desc()).first()
        nome_arquivo = zip_entry.nome_arquivo if zip_entry else "N/A"

        erros = []

        # Reexecuta validação para capturar mensagens (somente se inválido)
        if not validacao.geometria_valida:
            try:
                zip_stream = io.BytesIO(zip_entry.dados)
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(zip_stream, "r") as zip_ref:
                        zip_ref.extractall(tmpdir)

                    shp_path = None
                    for root, dirs, files in os.walk(tmpdir):
                        for file in files:
                            if file.endswith(".shp"):
                                shp_path = os.path.join(root, file)
                                break

                    if not shp_path:
                        erros.append("Arquivo .shp não encontrado no ZIP.")
                    else:
                        gdf = gpd.read_file(shp_path)

                        # EPSG
                        if not gdf.crs or gdf.crs.to_epsg() != 4674:
                            erros.append("EPSG inválido. Esperado: 4674.")

                        # Cod
                        if "Cod" not in gdf.columns:
                            erros.append("Campo obrigatório 'Cod' não encontrado.")
                        elif gdf["Cod"].isnull().any() or (gdf["Cod"].astype(str).str.strip() == "").any():
                            erros.append("Há valores nulos ou em branco no campo 'Cod'.")

                        # Geometria
                        if gdf["geometry"].isnull().any():
                            erros.append("Existem feições com geometria nula.")
                        elif not all(gdf.geometry.type.isin(["LineString", "MultiLineString"])):
                            erros.append("A geometria deve ser LINESTRING ou MULTILINESTRING.")
            except Exception as e:
                erros.append(f"Erro ao revalidar para relatório: {str(e)}")

        # 📝 Gerar PDF
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        largura, altura = A4

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, altura - 50, "Relatório de Importação e Validação de Geometria")

        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, altura - 80, f"Arquivo: {nome_arquivo}")
        pdf.drawString(50, altura - 95, f"Data da validação: {validacao.data_validacao.strftime('%d/%m/%Y %H:%M:%S')}")
        pdf.drawString(50, altura - 110, f"Resultado: {'VALIDADO COM SUCESSO' if validacao.geometria_valida else 'INVALIDADO'}")

        y = altura - 140
        pdf.drawString(50, y, "Detalhes:")
        y -= 20
        pdf.drawString(70, y, f"- Arquivos obrigatórios: {'Sim' if validacao.possui_arquivos_obrigatorios else 'Não'}")
        y -= 15
        pdf.drawString(70, y, f"- EPSG detectado: {validacao.epsg_detectado}")
        y -= 15
        pdf.drawString(70, y, f"- EPSG correto (4674): {'Sim' if validacao.epsg_correto else 'Não'}")
        y -= 15
        pdf.drawString(70, y, f"- Tipo de geometria: {validacao.tipo_geometria or 'Não identificado'}")
        y -= 15
        pdf.drawString(70, y, f"- Número de feições: {validacao.contagem_feicoes or 0}")

        if not validacao.geometria_valida:
            y -= 30
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(50, y, "Motivos da invalidação:")
            y -= 20
            pdf.setFont("Helvetica", 10)
            for erro in erros:
                pdf.drawString(70, y, f"- {erro}")
                y -= 15

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        return Response(content=buffer.read(), media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=relatorio_validacao.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")
