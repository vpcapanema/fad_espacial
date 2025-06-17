import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_usuario_sistema import UsuarioSistema
from app.models.cd_pessoa_fisica import PessoaFisica
from app.models.cd_pessoa_juridica import PessoaJuridica
from datetime import datetime

# Configurar templates
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

# ===== PÁGINA PRINCIPAL DO PAINEL MASTER =====

@router.get("/", response_class=HTMLResponse)
@router.get("", response_class=HTMLResponse)
def painel_master(request: Request, db: Session = Depends(get_db)):
    """Página principal do painel master"""
    print("[DEBUG PAINEL MASTER] Acessando painel master")
    
    # Verificar se o usuário está logado
    usuario_id = request.session.get("usuario_id")
    usuario_tipo = request.session.get("usuario_tipo")
    
    print(f"[DEBUG PAINEL MASTER] Redirecionando para login: usuario_id={usuario_id}, usuario_tipo={usuario_tipo}")
    
    if not usuario_id or usuario_tipo != "master":
        return RedirectResponse(url="/login", status_code=302)
    
    # Buscar dados do usuário logado
    usuario_logado = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("pn_painel_usuario_master.html", {
        "request": request,
        "usuario": usuario_logado
    })

# ===== ENDPOINTS PARA DADOS DAS TABELAS =====

@router.get("/dados/analistas", response_class=JSONResponse)
def listar_analistas_master(db: Session = Depends(get_db)):
    """Lista apenas usuários analistas para tabela do painel master"""
    analistas = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == "analista").all()
    return [
        {
            "id": u.id,
            "nome": u.nome,
            "cpf": u.cpf,
            "email": u.email,
            "telefone": u.telefone,
            "instituicao": u.instituicao,
            "tipo_lotacao": u.tipo_lotacao,
            "email_institucional": u.email_institucional,
            "telefone_institucional": u.telefone_institucional,
            "ramal": u.ramal,
            "sede_hierarquia": u.sede_hierarquia,
            "sede_coordenadoria": u.sede_coordenadoria,
            "sede_setor": u.sede_setor,
            "sede_assistencia": u.sede_assistencia,
            "regional_nome": u.regional_nome,
            "regional_coordenadoria": u.regional_coordenadoria,
            "regional_setor": u.regional_setor,
            "pessoa_fisica_id": u.pessoa_fisica_id,
            "criado_em": u.criado_em.strftime("%d/%m/%Y %H:%M") if u.criado_em else "",
            "aprovado_em": u.aprovado_em.strftime("%d/%m/%Y %H:%M") if u.aprovado_em else "",
            "aprovador_id": u.aprovador_id,
            "status": u.status,
            "ativo": u.ativo
        }
        for u in analistas
    ]

@router.get("/dados/coordenadores", response_class=JSONResponse)
def listar_coordenadores_master(db: Session = Depends(get_db)):
    """Lista apenas usuários coordenadores para tabela do painel master - CLONADO da função todos_usuarios"""
    coordenadores = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == "coordenador").all()
    return [
        {
            "id": u.id,
            "nome": u.nome,
            "cpf": u.cpf,
            "email": u.email,
            "telefone": u.telefone,
            "instituicao": u.instituicao,
            "tipo_lotacao": u.tipo_lotacao,
            "email_institucional": u.email_institucional,
            "telefone_institucional": u.telefone_institucional,
            "ramal": u.ramal,
            "tipo": u.tipo,
            "status": u.status,
            "ativo": u.ativo,
            "sede_hierarquia": u.sede_hierarquia,
            "sede_diretoria": u.sede_diretoria,
            "sede_coordenadoria_geral": u.sede_coordenadoria_geral,
            "sede_coordenadoria": u.sede_coordenadoria,
            "sede_assistencia": u.sede_assistencia,
            "regional_nome": u.regional_nome,
            "regional_coordenadoria": u.regional_coordenadoria,
            "regional_setor": u.regional_setor,
            "pessoa_fisica_id": u.pessoa_fisica_id,
            "criado_em": u.criado_em.strftime("%d/%m/%Y %H:%M") if u.criado_em else "",
            "aprovado_em": u.aprovado_em.strftime("%d/%m/%Y %H:%M") if u.aprovado_em else "",
            "aprovador_id": u.aprovador_id
        }
        for u in coordenadores
    ]

@router.get("/dados/todos-usuarios", response_class=JSONResponse)
def listar_todos_usuarios(db: Session = Depends(get_db)):
    """Lista todos os usuários do sistema para tabela do painel master"""
    usuarios = db.query(UsuarioSistema).all()
    return [
        {
            "id": u.id,
            "nome": u.nome,
            "cpf": u.cpf,
            "email": u.email,
            "telefone": u.telefone,
            "instituicao": u.instituicao,
            "tipo_lotacao": u.tipo_lotacao,
            "email_institucional": u.email_institucional,
            "telefone_institucional": u.telefone_institucional,
            "ramal": u.ramal,
            "tipo": u.tipo,
            "status": u.status,
            "ativo": u.ativo,
            "sede_hierarquia": u.sede_hierarquia,
            "sede_diretoria": u.sede_diretoria,
            "sede_coordenadoria_geral": u.sede_coordenadoria_geral,
            "sede_coordenadoria": u.sede_coordenadoria,
            "sede_assistencia": u.sede_assistencia,
            "regional_nome": u.regional_nome,
            "regional_coordenadoria": u.regional_coordenadoria,
            "regional_setor": u.regional_setor,
            "pessoa_fisica_id": u.pessoa_fisica_id,
            "criado_em": u.criado_em.strftime("%d/%m/%Y %H:%M") if u.criado_em else "",
            "aprovado_em": u.aprovado_em.strftime("%d/%m/%Y %H:%M") if u.aprovado_em else "",
            "aprovador_id": u.aprovador_id
        }
        for u in usuarios
    ]

# ===== ENDPOINTS PARA AÇÕES ADMINISTRATIVAS =====

@router.post("/acao/aprovar-usuario/{usuario_id}", response_class=JSONResponse)
def aprovar_usuario_master_acao(usuario_id: int, db: Session = Depends(get_db)):
    """Aprovar usuário"""
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado"})
    
    usuario.status = "aprovado"
    usuario.aprovado_em = datetime.now()
    db.commit()
    
    return {"detail": f"Usuário {usuario.nome} aprovado com sucesso"}

@router.post("/acao/reprovar-usuario/{usuario_id}", response_class=JSONResponse)
def reprovar_usuario_master_acao(usuario_id: int, db: Session = Depends(get_db)):
    """Reprovar usuário"""
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado"})
    
    usuario.status = "reprovado"
    db.commit()
    
    return {"detail": f"Usuário {usuario.nome} reprovado"}

@router.post("/acao/ativar-usuario/{usuario_id}", response_class=JSONResponse)
def ativar_usuario_master_acao(usuario_id: int, db: Session = Depends(get_db)):
    """Ativar usuário"""
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado"})
    
    usuario.ativo = True
    db.commit()
    
    return {"detail": f"Usuário {usuario.nome} ativado com sucesso"}

@router.post("/acao/desativar-usuario/{usuario_id}", response_class=JSONResponse)
def desativar_usuario_master(usuario_id: int, db: Session = Depends(get_db)):
    """Desativar usuário"""
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado"})
    
    usuario.ativo = False
    db.commit()
    
    return {"detail": f"Usuário {usuario.nome} desativado com sucesso"}
