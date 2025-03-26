from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.session import get_db
from app.api.dependencies import get_usuario_logado
from app.models.cd_usuario import CD_Usuario
from app.core.jinja import templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Página de login
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("cd_login.html", {"request": request})

# Processar login
@router.post("/login")
def login(request: Request, email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    print(f"\n🔍 Tentando login com: {email}")

    user = db.query(CD_Usuario).filter(CD_Usuario.email == email).first()

    if not user:
        print("❌ Usuário não encontrado no banco.")
        raise HTTPException(status_code=401, detail="Credenciais inválidas!")

    print("✅ Usuário encontrado.")

    print("🧪 Comparando senha enviada com hash armazenado:")
    print(f"Senha enviada: {senha}")
    print(f"Hash no banco: {user.senha_hash}")

    if not pwd_context.verify(senha, user.senha_hash):
        print("❌ Senha inválida.")
        raise HTTPException(status_code=401, detail="Credenciais inválidas!")

    print("✅ Senha válida.")

    if not user.aprovado:
        print("⚠️ Usuário não está aprovado.")
        raise HTTPException(status_code=403, detail="Aguardando aprovação do administrador!")

    print("🚀 Login autorizado! Iniciando sessão e redirecionando para /escolha.")
    request.session["usuario_id"] = user.id
    return RedirectResponse(url="/escolha", status_code=status.HTTP_303_SEE_OTHER)


# Página de cadastro
@router.get("/cadastro", response_class=HTMLResponse)
def cadastro_page(request: Request):
    return templates.TemplateResponse("cd_cadastro.html", {"request": request})

# Processar cadastro
@router.post("/cadastro")
def cadastro(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    if db.query(CD_Usuario).filter(CD_Usuario.email == email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    senha_hash = pwd_context.hash(senha)
    novo_usuario = CD_Usuario(nome=nome, email=email, senha_hash=senha_hash)
    db.add(novo_usuario)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# Painel (master ou usuário comum)
@router.get("/painel", response_class=HTMLResponse)
def painel(request: Request, usuario=Depends(get_usuario_logado), db: Session = Depends(get_db)):
    if usuario.tipo == "master":
        usuarios = db.query(CD_Usuario).filter(CD_Usuario.aprovado == False).all()
        return templates.TemplateResponse("cd_painel_master.html", {"request": request, "usuarios": usuarios})
    else:
        projetos = []  # futuramente: buscar projetos reais
        return templates.TemplateResponse("cd_painel_usuario.html", {"request": request, "usuario": usuario, "projetos": projetos})

# Aprovação de usuários pelo master
@router.post("/aprovar-usuario")
def aprovar_usuario(usuario_id: int = Form(...), db: Session = Depends(get_db)):
    usuario = db.query(CD_Usuario).filter(CD_Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado!")
    usuario.aprovado = True
    db.commit()
    return RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)

# Logout
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

# NOVO: Tela de escolha após login
@router.get("/escolha", response_class=HTMLResponse)
def escolha_pos_login(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)

    usuario = db.query(CD_Usuario).filter(CD_Usuario.id == usuario_id).first()
    if not usuario or not usuario.aprovado:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("cd_escolha_pos_login.html", {
        "request": request,
        "usuario": usuario
    })
