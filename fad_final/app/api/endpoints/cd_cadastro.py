from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.jinja import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def form_cadastro(request: Request):
    return templates.TemplateResponse("cd_cadastro_form.html", {"request": request})

@router.post("/cadastro/pf")
async def cadastrar_pf(
    cpf: str = Form(...),
    nome: str = Form(...),
    email: str = Form(...),
    celular: str = Form(...)
):
    if not cpf or not nome or not email or not celular:
        return JSONResponse(content={"sucesso": False})
    return JSONResponse(content={"sucesso": True})

@router.post("/cadastro/pj")
async def cadastrar_pj(
    cnpj: str = Form(...),
    razao_social: str = Form(...),
    nome_fantasia: str = Form(...),
    rua: str = Form(...),
    numero: str = Form(...),
    complemento: str = Form(...),
    bairro: str = Form(...),
    cep: str = Form(...),
    cidade: str = Form(...),
    uf: str = Form(...)
):
    if not cnpj or not razao_social:
        return JSONResponse(content={"sucesso": False})
    return JSONResponse(content={"sucesso": True})
