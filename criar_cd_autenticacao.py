import os

base_dir = "app"

arquivos = {
    f"{base_dir}/models/cd_usuario.py": """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.base import Base
from datetime import datetime

class CD_Usuario(Base):
    __tablename__ = 'usuarios_sistema'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)
    tipo = Column(String, default='usuario')  # 'master' ou 'usuario'
    aprovado = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
""",

    f"{base_dir}/api/endpoints/cd_autenticacao.py": """from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.cd_usuario import CD_Usuario
from passlib.context import CryptContext

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
""",

    f"{base_dir}/templates/cd_login.html": """<!DOCTYPE html>
<html lang=\"pt\">
<head>
    <meta charset=\"UTF-8\">
    <title>Login - FAD</title>
</head>
<body>
    <h1>Login na FAD</h1>
    <form action=\"/login\" method=\"post\">
        <input type=\"email\" name=\"email\" placeholder=\"Email\" required><br>
        <input type=\"password\" name=\"senha\" placeholder=\"Senha\" required><br>
        <button type=\"submit\">Entrar</button>
    </form>
    <p>Não possui conta? <a href=\"/cadastro\">Cadastre-se</a></p>
</body>
</html>
""",

    f"{base_dir}/templates/cd_cadastro.html": """<!DOCTYPE html>
<html lang=\"pt\">
<head>
    <meta charset=\"UTF-8\">
    <title>Cadastro - FAD</title>
</head>
<body>
    <h1>Cadastro de Novo Usuário</h1>
    <form action=\"/cadastro\" method=\"post\">
        <input type=\"text\" name=\"nome\" placeholder=\"Nome completo\" required><br>
        <input type=\"email\" name=\"email\" placeholder=\"Email\" required><br>
        <input type=\"password\" name=\"senha\" placeholder=\"Senha\" required><br>
        <button type=\"submit\">Cadastrar</button>
    </form>
</body>
</html>
""",

    f"{base_dir}/templates/cd_painel.html": """<!DOCTYPE html>
<html lang=\"pt\">
<head>
    <meta charset=\"UTF-8\">
    <title>Painel do Usuário</title>
</head>
<body>
    <h1>Bem-vindo {{ usuario.nome }}</h1>
    <h2>Seus projetos rodados na FAD</h2>
    {% if projetos %}
        <ul>
        {% for projeto in projetos %}
            <li>{{ projeto.nome }} - {{ projeto.data }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>Você ainda não possui projetos cadastrados.</p>
    {% endif %}
</body>
</html>
"""
}

for caminho, conteudo in arquivos.items():
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)

print("✅ Estrutura de autenticação criada com sucesso!")
