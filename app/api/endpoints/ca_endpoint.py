from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, get_db
from app.modules.conformidade_ambiental.ca_processador import processar_conformidade
from app.models.pr_projeto import Projeto

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# Rota para exibir a interface com os projetos
@router.get("/importar-validar", response_class=HTMLResponse)
def exibir_interface_validacao(request: Request, db: Session = Depends(get_db)):
    projetos = db.query(Projeto).order_by(Projeto.nome.asc()).all()
    return templates.TemplateResponse("iv_interface.html", {
        "request": request,
        "projetos": projetos
    })


# Rota para executar a análise de conformidade (POST)
@router.post("/", response_class=JSONResponse)
async def executar_conformidade(request: Request):
    data = await request.json()
    camadas = data.get("camadas", [])
    tipo_laudo = data.get("tipo_laudo", "analitico")

    resultado = processar_conformidade({
        "camadas": camadas,
        "tipo_laudo": tipo_laudo
    })

    return JSONResponse(content=resultado)


# Rota para buscar o nome do último arquivo validado
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
