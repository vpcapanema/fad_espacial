from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

router = APIRouter(prefix="/download", tags=["Download"])

@router.get("/shapefile-teste")
def download_shapefile_teste():
    """
    Download do shapefile de teste para validação do sistema
    """
    arquivo_zip = "trecho_rodoviario_teste.zip"
    caminho_completo = Path(__file__).parent.parent.parent / arquivo_zip
    
    if not caminho_completo.exists():
        raise HTTPException(status_code=404, detail="Arquivo de teste não encontrado")
    
    return FileResponse(
        path=str(caminho_completo),
        filename=arquivo_zip,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={arquivo_zip}"}
    )
