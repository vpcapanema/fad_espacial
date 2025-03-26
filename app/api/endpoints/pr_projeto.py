from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import get_db
from app.models.pr_projeto import Projeto
from app.models.cd_interessado import InteressadoPF, InteressadoPJ, InteressadoTrecho
from app.core.jinja import templates

router = APIRouter()

# Página de cadastro de projeto
@router.get("/projeto/cadastrar", response_class=HTMLResponse)
def exibir_formulario_projeto(request: Request, db: Session = Depends(get_db)):
    pjs = db.query(InteressadoPJ).all()
    pfs = db.query(InteressadoPF).all()
    trechos = db.query(InteressadoTrecho).all()
    return templates.TemplateResponse("pr_cadastro_projeto.html", {
        "request": request,
        "pjs": pjs,
        "pfs": pfs,
        "trechos": trechos
    })


# Processar cadastro de projeto
@router.post("/projeto/salvar")
def salvar_projeto(
    request: Request,
    nome: str = Form(...),
    interessado_id: int = Form(...),
    representante_id: int = Form(...),
    trecho_id: int = Form(...),
    modulos: str = Form(...),
    db: Session = Depends(get_db)
):
    novo_projeto = Projeto(
        nome=nome,
        interessado_id=interessado_id,
        representante_id=representante_id,
        trecho_id=trecho_id,
        modulos_selecionados=modulos
    )
    db.add(novo_projeto)
    db.commit()
    db.refresh(novo_projeto)

    modulos_lista = [int(m) for m in modulos.split(",")]
    if set(modulos_lista).issubset({4}):  # Apenas módulo 4
        return RedirectResponse(url="/modulo4", status_code=303)
    else:
        return RedirectResponse(url="/importar-validar", status_code=303)


# NOVO: associar nome do arquivo ao projeto após validação
@router.post("/projeto/atualizar-arquivo")
async def atualizar_arquivo_do_projeto(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    projeto_id = data.get("projeto_id")
    nome_arquivo = data.get("arquivo")

    if not projeto_id or not nome_arquivo:
        raise HTTPException(status_code=400, detail="Dados incompletos")

    projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    resultado = db.execute(text("""
        UPDATE validacao_geometria
        SET projeto_id = :projeto_id
        WHERE nome_arquivo = :nome_arquivo
          AND geometria_valida = TRUE
        RETURNING id
    """), {
        "projeto_id": projeto_id,
        "nome_arquivo": nome_arquivo
    })

    db.commit()
    updated = resultado.fetchone()
    if updated:
        return JSONResponse(content={"sucesso": True})
    else:
        raise HTTPException(status_code=404, detail="Geometria não encontrada ou inválida")
