from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.validacao_service import ValidacaoService
import tempfile
import json

router = APIRouter(prefix="/api/projeto", tags=["Projeto Novo"])

@router.post("/validar")
async def validar_completo(arquivo_zip: UploadFile = File(...), db: Session = Depends(get_db)):
    """Fluxo completo de validação"""
    
    # Validar ZIP  
    resultado = ValidacaoService.validar_zip(arquivo_zip)
    
    if resultado["status"] == "erro":
        return JSONResponse({
            "status": "erro",
            "etapa": "zip",
            "mensagem": resultado["erro"], 
            "pdf_relatorio": resultado["pdf_relatorio"]
        })
    
    # Validar geometria
    resultado_geom = ValidacaoService.validar_geometria(
        resultado["shp_file"], 
        resultado["upload_id"]
    )
    
    return JSONResponse({
        "status": resultado_geom["status"],
        "mensagem": "Sucesso!" if resultado_geom["status"] == "sucesso" else resultado_geom["erro"],
        "upload_id": resultado["upload_id"],
        "pdf_relatorio": resultado_geom["pdf_relatorio"],
        "geometria_wkt": resultado_geom.get("geometria_wkt")
    })

@router.get("/mapa/{upload_id}")
async def carregar_mapa(upload_id: str):
    """Carrega dados para o mapa"""
    
    # Geometria validada (simulada)
    geometria_wkt = "POLYGON((-46.5 -23.5, -46.4 -23.5, -46.4 -23.4, -46.5 -23.4, -46.5 -23.5))"
    
    # Malha DER (simulada) 
    malha_der = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"rodovia": "SP-348"},
            "geometry": {
                "type": "LineString", 
                "coordinates": [[-46.6, -23.5], [-46.5, -23.4]]
            }
        }]
    }
    
    return JSONResponse({
        "status": "sucesso",
        "geometria_wkt": geometria_wkt,
        "malha_der": malha_der
    })

@router.post("/croqui")
async def gerar_croqui(dados: dict):
    """Gera croqui"""
    
    import uuid
    croqui_id = str(uuid.uuid4())[:8]
    
    return JSONResponse({
        "status": "sucesso",
        "caminho_croqui": f"/static/images/croqui_{croqui_id}.svg",
        "mensagem": "Croqui gerado!"
    })

@router.post("/finalizar")
async def finalizar_projeto(dados: dict):
    """Finaliza projeto"""
    
    import uuid
    codigo = f"PROJ-{str(uuid.uuid4())[:8].upper()}"
    
    return JSONResponse({
        "status": "sucesso",
        "codigo_projeto": codigo,
        "pdf_final": f"/static/relatorios/final_{codigo}.pdf",
        "mensagem": f"Projeto {codigo} finalizado!"
    })
