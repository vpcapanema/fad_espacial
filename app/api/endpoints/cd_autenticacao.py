from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.cd_usuario import CD_Usuario
from passlib.context import CryptContext
from app.api.endpoints.cd_autenticacao import router as auth_router  # 👈 NOVO

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("cd_login.html", {"request": request})

@router.post("/login")
def login(request: Request, email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(CD_Usuario).filter(CD_Usuario.email == email).first()
    if not user or not pwd_context.verify(senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not user.aprovado:
        raise HTTPException(status_code=403, detail="Aguardando aprovação do administrador.")
    response = RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("usuario_id", str(user.id))
    return response

@router.get("/cadastro", response_class=HTMLResponse)
def cadastro_page(request: Request):
    return templates.TemplateResponse("cd_cadastro.html", {"request": request})

@router.post("/cadastro")
def cadastro(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    if db.query(CD_Usuario).filter(CD_Usuario.email == email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo_usuario = CD_Usuario(
        nome=nome,
        email=email,
        senha_hash=pwd_context.hash(senha),
        tipo="usuario",
        aprovado=False
    )
    db.add(novo_usuario)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/painel", response_class=HTMLResponse)
def painel_usuario(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse("/login")
    usuario = db.query(CD_Usuario).filter(CD_Usuario.id == int(usuario_id)).first()
    return templates.TemplateResponse("cd_painel.html", {"request": request, "usuario": usuario, "projetos": []})
