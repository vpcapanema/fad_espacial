from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def interface_conformidade(request: Request):
    return templates.TemplateResponse("ca_interface.html", {"request": request})

from fastapi import Request
from fastapi.responses import JSONResponse

@router.post("/", response_class=JSONResponse)
async def executar_conformidade(request: Request):
    data = await request.json()
    camadas = data.get("camadas", [])
    tipo_laudo = data.get("tipo_laudo", "analitico")

    # Aqui você chama seu processador real
    from app.modules.conformidade_ambiental.ca_processador import processar_conformidade
    resultado = processar_conformidade({"camadas": camadas, "tipo_laudo": tipo_laudo})

    return JSONResponse(content=resultado)
from sqlalchemy import text
from app.database.session import SessionLocal

@router.get("/arquivo-atual")
def nome_arquivo_validado():
    session = SessionLocal()
    try:
        resultado = session.execute(text("""
            SELECT nome_arquivo
            FROM validacao_geometria
            WHERE geometria_valida = TRUE
            ORDER BY data_validacao DESC
            LIMIT 1
        """)).fetchone()

        if resultado:
            return {"arquivo": resultado[0]}
        else:
            return {"arquivo": "Nenhum arquivo validado encontrado"}

    finally:
        session.close()
