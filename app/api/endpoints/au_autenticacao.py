from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException
from app.database.session import get_db
from app.models.cd_usuario_sistema import UsuarioSistema
from app.security.hashing import verificar_senha
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
import time
from datetime import datetime # Adicionado import

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

templates = Jinja2Templates(directory="app/templates")

# ✅ Processa os dados do formulário de login
@router.post("")
@router.post("/")
def login_usuario(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    tipo: str = Form(...),
    db: Session = Depends(get_db)
):
    start = time.time()
    print(f"[DEBUG LOGIN] Tentativa de login para: {email} como {tipo}")
    
    # Busca apenas os campos necessários para autenticação
    # Modificado para buscar por email E tipo, pois pode haver múltiplos usuários do mesmo email
    usuario = db.query(UsuarioSistema.id, UsuarioSistema.email, UsuarioSistema.senha_hash, UsuarioSistema.status, UsuarioSistema.ativo, UsuarioSistema.tipo, UsuarioSistema.nome, UsuarioSistema.cpf).filter(
        UsuarioSistema.email == email,
        UsuarioSistema.tipo == tipo
    ).first()

    if not usuario:
        return JSONResponse(status_code=401, content={"detail": "email_tipo", "message": "E-mail não encontrado para o tipo de acesso selecionado."})

    print(f"[DEBUG LOGIN] Usuário encontrado: {usuario.nome}, CPF: {usuario.cpf}, Status: {usuario.status}, Ativo: {usuario.ativo}, Tipo: {usuario.tipo}")

    # bcrypt é seguro, mas pode ser lento. Se possível, use um custo menor ao gerar os hashes.
    if not bcrypt.verify(senha, usuario.senha_hash):
        return JSONResponse(status_code=401, content={"detail": "senha", "message": "Senha incorreta. Tente novamente."})

    if usuario.status != "aprovado":
        status_alias = {
            "aguardando aprovação": "Aguardando aprovação",
            "reprovado": "Reprovado",
            "aprovado": "Aprovado"
        }
        status_legivel = status_alias.get(usuario.status, usuario.status.capitalize())
        return JSONResponse(status_code=403, content={"detail": "status", "message": f"Status do cadastro: '{status_legivel}'. O acesso só é permitido para usuários aprovados."})
    if not usuario.ativo:
        return JSONResponse(status_code=403, content={"detail": "ativo", "message": "Cadastro não está ativado. Entre em contato com o suporte."})
    if usuario.tipo != tipo:
        return JSONResponse(status_code=401, content={"detail": "tipo", "message": "Tipo de acesso incorreto para este usuário."})
    # Verifica se o SessionMiddleware está presente
    if not hasattr(request, "session"):
        return JSONResponse(status_code=500, content={"detail": "SessionMiddleware não configurado", "message": "Erro interno. Tente novamente mais tarde."})

    # Salva todos os dados essenciais na sessão
    request.session.clear()
    request.session["usuario_id"] = usuario.id
    request.session["usuario_tipo"] = usuario.tipo
    request.session["usuario_nome"] = usuario.nome
    request.session["usuario_email"] = usuario.email
    request.session["last_active"] = int(datetime.utcnow().timestamp()) # CORRIGIDO

    # Redireciona conforme o tipo
    if usuario.tipo == "master":
        destino = "/painel-master/"
    elif usuario.tipo == "coordenador":
        destino = "/painel-coordenador/"
    else:
        destino = "/painel-analista/"

    tempo = round((time.time() - start)*1000)
    print(f"Login processado em {tempo} ms para {email}")
    return JSONResponse(status_code=200, content={"redirect": destino})

# ❎ Rota de logout (encerra a sessão e redireciona para login)
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

@router.post("/tipos-acesso")
def tipos_acesso_por_email(email: str = Form(...), db: Session = Depends(get_db)):
    """Retorna os tipos de acesso disponíveis para o e-mail informado, com alias bonitos."""
    tipos = db.query(UsuarioSistema.tipo).filter(UsuarioSistema.email == email).distinct().all()
    alias = {
        "analista": "Analista (Acesso Técnico)",
        "coordenador": "Coordenador (Gestão)",
        "master": "Master (Administrador Geral)"
    }
    return [{"value": t[0], "label": alias.get(t[0], t[0].capitalize())} for t in tipos]
