from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core.jinja import templates
from app.database.session import SessionLocal
from app.models.cd_usuario import CD_Usuario

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependência de sessão de banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Interface HTML
@router.get("/cadastro", response_class=HTMLResponse)
async def form_cadastro(request: Request):
    return templates.TemplateResponse("cd_cadastro.html", {"request": request})

# Cadastro de novo usuário
@router.post("/registrar")
def registrar_usuario(
    request: Request,
    nome: str = Form(...),
    cpf: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    tipo_usuario: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verifica se CPF já existe
    usuario_existente = db.query(CD_Usuario).filter(CD_Usuario.cpf == cpf).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário cadastrado com este CPF."
        )

    # Cria hash seguro da senha
    senha_hash = pwd_context.hash(senha)

    novo_usuario = CD_Usuario(
        nome=nome,
        cpf=cpf,
        email=email,
        senha_hash=senha_hash,
        tipo=tipo_usuario,
        aprovado=False
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {"mensagem": "Cadastro realizado com sucesso. Aguardando aprovação do administrador."}
