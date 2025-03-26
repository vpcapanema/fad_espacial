from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.geometrias import Geometria
from app.relatorios.relatorio_upload import gerar_relatorio_upload
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import io
import zipfile
import geopandas as gpd
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
async def upload_arquivo(arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if not arquivo.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="O arquivo deve ser um ZIP.")

        if arquivo.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="O arquivo é muito grande. O tamanho máximo permitido é 100 MB.")

        conteudo_zip = await arquivo.read()
        zip_stream = io.BytesIO(conteudo_zip)

        with zipfile.ZipFile(zip_stream, 'r') as zip_ref:
            arquivos_no_zip = zip_ref.namelist()
            shapefile = next((arquivo for arquivo in arquivos_no_zip if arquivo.endswith('.shp')), None)

            if not shapefile:
                raise HTTPException(status_code=400, detail="O arquivo ZIP deve conter um shapefile (.shp).")

            zip_ref.extractall("/tmp/shapefile")
            gdf = gpd.read_file(f"/tmp/shapefile/{shapefile}")

            if gdf.crs is None:
                raise HTTPException(status_code=400, detail="O shapefile não tem um sistema de coordenadas (CRS) definido.")

            if gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            for _, row in gdf.iterrows():
                nova_geometria = Geometria(
                    nome=arquivo.filename,
                    geometria=row.geometry.wkt
                )
                db.add(nova_geometria)
            db.commit()

        relatorio_path = "/tmp/relatorio_upload.pdf"
        gerar_relatorio_upload(
            nome_arquivo=arquivo.filename,
            tamanho_bytes=len(conteudo_zip),
            epsg=4326,
            quantidade=len(gdf),
            sucesso=True,
            caminho_destino=relatorio_path
        )

        return JSONResponse(content={
            "mensagem": "Shapefile importado e geometrias armazenadas com sucesso!",
            "sucesso": True,
            "dados": {"quantidade_geometrias": len(gdf)}
        })

    except HTTPException as e:
        logger.error(f"Erro HTTP: {e.detail}")
        raise e

    except zipfile.BadZipFile:
        logger.error("Arquivo ZIP inválido.")
        raise HTTPException(status_code=400, detail="O arquivo não é um ZIP válido.")

    except Exception as e:
        logger.error(f"Erro interno: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno ao processar o arquivo.")

@router.get("/upload/relatorio")
def baixar_relatorio_upload():
    caminho = "/tmp/relatorio_upload.pdf"
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Relatório de upload não encontrado.")
    return FileResponse(caminho, filename="relatorio_upload.pdf", media_type="application/pdf")
