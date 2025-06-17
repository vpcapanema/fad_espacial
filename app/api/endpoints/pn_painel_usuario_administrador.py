from pydoc import text
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_usuario_sistema import UsuarioSistema
from app.core.session_control import session_manager

router = APIRouter(
    prefix='/painel-coordenador',
    tags=['Painel do Coordenador']
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def painel_coordenador(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=302)
    usuario = db.query(UsuarioSistema).filter_by(id=usuario_id).first()
    session_status = session_manager.check_session_validity(request)
    tempo_restante = int(session_status.get('remaining_seconds', 0))
    return templates.TemplateResponse("pn_painel_usuario_administrador.html", {
        "request": request,
        "usuario": usuario,
        "tempo_restante": tempo_restante
    })

@router.get('/projetos')
def listar_projetos(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=302)
    
    query = text("""
        SELECT p.id, p.nome,
               COALESCE(pj.razao_social, pf.nome) AS interessado,
               rep.nome AS representante,
               cad.nome AS cadastrante,
               COALESCE(p.status, 'rascunho') AS status
        FROM projeto p
        LEFT JOIN "Cadastro".pessoa_juridica pj ON pj.id = p.pessoa_juridica_id
        LEFT JOIN "Cadastro".pessoa_fisica pf ON pf.id = p.pessoa_fisica_id
        LEFT JOIN "Cadastro".usuario_sistema rep ON rep.id = p.representante_id
        LEFT JOIN "Cadastro".usuario_sistema cad ON cad.id = p.usuario_id
        ORDER BY p.id DESC
    """)
    projetos = db.execute(query).fetchall()
    return [dict(row) for row in projetos]

@router.get('/usuarios')
def listar_usuarios_coordenador(request: Request, db: Session = Depends(get_db)):
    """Lista usuários coordenadores para o painel master"""
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=302)
    
    # Buscar usuários coordenadores
    coordenadores = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == "coordenador").all()
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "email": c.email,
            "telefone": c.telefone,
            "instituicao": c.instituicao,
            "tipo_lotacao": c.tipo_lotacao,
            "email_institucional": c.email_institucional,
            "telefone_institucional": c.telefone_institucional,
            "ramal": c.ramal,
            "sede_hierarquia": c.sede_hierarquia,
            "sede_coordenadoria": c.sede_coordenadoria,
            "sede_setor": c.sede_setor,
            "sede_assistencia": c.sede_assistencia,
            "regional_nome": c.regional_nome,
            "regional_coordenadoria": c.regional_coordenadoria,
            "regional_setor": c.regional_setor,
            "pessoa_fisica_id": c.pessoa_fisica_id,
            "criado_em": c.criado_em.strftime("%Y-%m-%d %H:%M:%S") if c.criado_em else "",
            "aprovado_em": c.aprovado_em.strftime("%Y-%m-%d %H:%M:%S") if c.aprovado_em else "",
            "aprovador_id": c.aprovador_id,
            "status": c.status,
            "ativo": c.ativo
        }
        for c in coordenadores
    ]
