from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.session import get_db
from app.api.dependencies import get_usuario_logado
from app.models.cd_usuario import CD_Usuario

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("cd_login.html", {"request": request})

@router.post("/login")
def login(request: Request, email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(CD_Usuario).filter(CD_Usuario.email == email).first()
    if not user or not pwd_context.verify(senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas!")
    if not user.aprovado:
        raise HTTPException(status_code=403, detail="Aguardando aprovação do administrador!")
    
    request.session["usuario_id"] = user.id
    return RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/cadastro", response_class=HTMLResponse)
def cadastro_page(request: Request):
    return templates.TemplateResponse("cd_cadastro.html", {"request": request})

@router.post("/cadastro")
def cadastro(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    if db.query(CD_Usuario).filter(CD_Usuario.email == email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    senha_hash = pwd_context.hash(senha)
    novo_usuario = CD_Usuario(nome=nome, email=email, senha_hash=senha_hash)
    db.add(novo_usuario)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/painel", response_class=HTMLResponse)
def painel(request: Request, usuario=Depends(get_usuario_logado), db: Session = Depends(get_db)):
    if usuario.tipo == "master":
        usuarios = db.query(CD_Usuario).filter(CD_Usuario.aprovado == False).all()
        return templates.TemplateResponse("cd_painel_master.html", {"request": request, "usuarios": usuarios})
    else:
        projetos = []  # futuramente: buscar projetos reais
        return templates.TemplateResponse("cd_painel_usuario.html", {"request": request, "usuario": usuario, "projetos": projetos})

@router.post("/aprovar-usuario")
def aprovar_usuario(usuario_id: int = Form(...), db: Session = Depends(get_db)):
    usuario = db.query(CD_Usuario).filter(CD_Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado!")
    usuario.aprovado = True
    db.commit()
    return RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
