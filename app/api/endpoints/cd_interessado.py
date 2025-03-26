from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.jinja import templates
from app.models.cd_usuario import CD_Usuario
from app.models.cd_interessado import InteressadoPF, InteressadoPJ, InteressadoTrecho

router = APIRouter()

# Verificação de sessão
def get_usuario(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")
    usuario = db.query(CD_Usuario).filter(CD_Usuario.id == usuario_id).first()
    if not usuario or not usuario.aprovado:
        raise HTTPException(status_code=403, detail="Acesso negado.")
    return usuario

# Formulário PF
@router.get("/cadastro/interessado/pf", response_class=HTMLResponse)
def form_pf(request: Request, usuario=Depends(get_usuario)):
    return templates.TemplateResponse("cd_interessado_pf.html", {"request": request})

# Submissão PF
@router.post("/cadastro/interessado/pf")
def salvar_pf(
    request: Request,
    nome: str = Form(...),
    cpf: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.query(InteressadoPF).filter(InteressadoPF.cpf == cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado.")
    pf = InteressadoPF(nome=nome, cpf=cpf, email=email, telefone=telefone)
    db.add(pf)
    db.commit()
    return JSONResponse(content={"mensagem": "PF salvo com sucesso"})

# Formulário PJ
@router.get("/cadastro/interessado/pj", response_class=HTMLResponse)
def form_pj(request: Request, usuario=Depends(get_usuario)):
    return templates.TemplateResponse("cd_interessado_pj.html", {"request": request})

# Submissão PJ
@router.post("/cadastro/interessado/pj")
def salvar_pj(
    request: Request,
    razao_social: str = Form(...),
    cnpj: str = Form(...),
    nome_fantasia: str = Form(None),
    email: str = Form(None),
    telefone: str = Form(None),
    rua: str = Form(None),
    numero: str = Form(None),
    complemento: str = Form(None),
    bairro: str = Form(None),
    cep: str = Form(None),
    cidade: str = Form(None),
    uf: str = Form(None),
    db: Session = Depends(get_db)
):
    if db.query(InteressadoPJ).filter(InteressadoPJ.cnpj == cnpj).first():
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado.")
    pj = InteressadoPJ(
        razao_social=razao_social,
        cnpj=cnpj,
        nome_fantasia=nome_fantasia,
        email=email,
        telefone=telefone,
        rua=rua,
        numero=numero,
        complemento=complemento,
        bairro=bairro,
        cep=cep,
        cidade=cidade,
        uf=uf
    )
    db.add(pj)
    db.commit()
    return JSONResponse(content={"mensagem": "PJ salvo com sucesso"})

# Formulário Trecho
@router.get("/cadastro/interessado/trecho", response_class=HTMLResponse)
def form_trecho(request: Request, usuario=Depends(get_usuario)):
    return templates.TemplateResponse("cd_interessado_trecho.html", {"request": request})

# Submissão Trecho
@router.post("/cadastro/interessado/trecho")
def salvar_trecho(
    request: Request,
    codigo: str = Form(...),
    denominacao: str = Form(...),
    municipio: str = Form(...),
    db: Session = Depends(get_db)
):
    trecho = InteressadoTrecho(codigo=codigo, denominacao=denominacao, municipio=municipio)
    db.add(trecho)
    db.commit()
    return JSONResponse(content={"mensagem": "Trecho salvo com sucesso"})
