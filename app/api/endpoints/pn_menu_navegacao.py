from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_pessoa_fisica import PessoaFisica
from app.models.cd_pessoa_juridica import PessoaJuridica
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from fastapi.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/geo-de-obra")
def geo_de_obra(request: Request):
    return templates.TemplateResponse("pagina_em_construcao.html", {"request": request, "modulo": "Geo de Obra"})

@router.get("/cadastrar-trechos")
def cadastrar_trechos(request: Request):
    return templates.TemplateResponse("cd_trecho.html", {"request": request})

@router.get("/favorabilidade-multicriterio")
def fav_multicriterio(request: Request):
    return templates.TemplateResponse("pagina_em_construcao.html", {"request": request, "modulo": "Favorabilidade Multicritério"})

@router.get("/favorabilidade-socioeconomica")
def fav_socioeconomica(request: Request):
    return templates.TemplateResponse("pagina_em_construcao.html", {"request": request, "modulo": "Favorabilidade Socioeconômica"})

@router.get("/favorabilidade-infraestrutural")
def fav_infra(request: Request):
    return templates.TemplateResponse("pagina_em_construcao.html", {"request": request, "modulo": "Favorabilidade Infraestrutural"})

@router.get("/conformidade")
def conformidade(request: Request):
    return templates.TemplateResponse("ca_interface.html", {"request": request})

@router.get("/pessoa-fisica")
def pessoa_fisica(request: Request):
    return templates.TemplateResponse("cd_interessado_pf.html", {"request": request})

@router.get("/pessoa-juridica")
def pessoa_juridica(request: Request):
    return templates.TemplateResponse("cd_interessado_pj.html", {"request": request})

@router.get("/usuario")
def cadastro_usuario(request: Request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("cd_cadastro_usuario.html", {"request": request})

@router.get("/projeto")
def cadastro_projeto(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=302)
    pfs = db.query(PessoaFisica).all()
    pjs = db.query(PessoaJuridica).all()
    trechos = db.query(TrechoEstadualizacao).all()
    return templates.TemplateResponse("pr_cadastro_projeto.html", {
        "request": request,
        "pfs": pfs,
        "pjs": pjs,
        "trechos": trechos
    })
