from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.database.session import get_db
from app.models.cd_usuario_sistema import UsuarioSistema
from app.models.cd_pessoa_fisica import PessoaFisica
from app.models.cd_pessoa_juridica import PessoaJuridica
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from app.models.cd_rodovia_estadualizacao import RodoviaEstadualizacao
from app.models.cd_dispositivo_estadualizacao import DispositivoEstadualizacao
from app.models.cd_obra_arte_estadualizacao import ObraArteEstadualizacao
from app.core.session_control import session_manager

router = APIRouter(
    tags=['Painel Master']
)
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def painel_master(request: Request, db: Session = Depends(get_db)):
    print(f"[DEBUG PAINEL MASTER] Acessando painel master")
    usuario_id = request.session.get("usuario_id")
    usuario_tipo = request.session.get("usuario_tipo")
    if not usuario_id or usuario_tipo != "master":
        print(f"[DEBUG PAINEL MASTER] Redirecionando para login: usuario_id={usuario_id}, usuario_tipo={usuario_tipo}")
        return RedirectResponse(url="/login", status_code=302)
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    print(f"[DEBUG PAINEL MASTER] usuario_id: {usuario_id}, usuario_tipo: {usuario_tipo}, usuario_nome: {usuario.nome if usuario else 'N/A'}")
    
    if not usuario:
        print(f"[DEBUG PAINEL MASTER] Redirecionando para login: usuário não encontrado")
        return RedirectResponse(url="/login", status_code=302)
    
    if usuario.tipo != "master":
        print(f"[DEBUG PAINEL MASTER] Redirecionando para login: tipo incorreto {usuario.tipo}")
        return RedirectResponse(url="/login", status_code=302)    
    
    # Carregar dados de todas as tabelas para o painel
    print(f"[DEBUG PAINEL MASTER] Carregando dados para usuário: {usuario.nome}")
      # Estatísticas gerais
    total_usuarios = db.query(UsuarioSistema).count()
    total_pf = db.query(PessoaFisica).count()
    total_pj = db.query(PessoaJuridica).count()
    total_trechos = db.query(TrechoEstadualizacao).count()
    
    # Elementos rodoviários
    total_rodovias = db.query(RodoviaEstadualizacao).count()
    total_dispositivos = db.query(DispositivoEstadualizacao).count() 
    total_obras_arte = db.query(ObraArteEstadualizacao).count()
    
    # Usuários por tipo
    usuarios_master = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == "master").count()
    usuarios_coordenador = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == "coordenador").count()
    usuarios_analista = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == "analista").count()
    
    # Usuários por status
    usuarios_aprovados = db.query(UsuarioSistema).filter(UsuarioSistema.status == "aprovado").count()
    usuarios_pendentes = db.query(UsuarioSistema).filter(UsuarioSistema.status == "aguardando aprovação").count()
    usuarios_ativos = db.query(UsuarioSistema).filter(UsuarioSistema.ativo == True).count()
    
    print(f"[DEBUG PAINEL MASTER] Carregando painel para usuário: {usuario.nome}")
    # Tempo real de sessão
    session_status = session_manager.check_session_validity(request)
    tempo_restante = int(session_status.get('remaining_seconds', 0))
    return templates.TemplateResponse("pn_painel_usuario_master.html", {
        "request": request,
        "usuario": usuario,
        "data_hoje": date.today().strftime("%d/%m/%Y"),
        "tempo_restante": tempo_restante,
          # Estatísticas gerais
        "total_usuarios": total_usuarios,
        "total_pf": total_pf,
        "total_pj": total_pj,
        "total_trechos": total_trechos,
        
        # Elementos rodoviários
        "total_rodovias": total_rodovias,
        "total_dispositivos": total_dispositivos,
        "total_obras_arte": total_obras_arte,
        
        # Usuários por tipo
        "usuarios_master": usuarios_master,
        "usuarios_coordenador": usuarios_coordenador,
        "usuarios_analista": usuarios_analista,
        
        # Usuários por status
        "usuarios_aprovados": usuarios_aprovados,
        "usuarios_pendentes": usuarios_pendentes,
        "usuarios_ativos": usuarios_ativos
    })

@router.get("/dados/analistas", response_class=JSONResponse)
def listar_analistas(db: Session = Depends(get_db)):
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
            "tipo": u.tipo,
            "status": u.status,
            "ativo": "Sim" if u.ativo else "Não",
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
        }        for u in analistas
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

@router.post("/es/aprovar/{usuario_id}")
def aprovar_coordenador(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario.status = "Aprovado"
    usuario.ativo = True
    db.commit()
    return {"mensagem": "Coordenador aprovado com sucesso."}

@router.post("/es/reprovar/{usuario_id}")
def reprovar_coordenador(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario.status = "Reprovado"
    usuario.ativo = False
    db.commit()
    return {"mensagem": "Coordenador reprovado com sucesso."}

@router.post("/ativar/{usuario_id}", response_class=JSONResponse)
def ativar_usuario_master(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado."})
    usuario.ativo = True
    db.commit()
    return {"detail": "Usuário ativado com sucesso"}

@router.get("/painel-master", response_class=HTMLResponse)
def painel_master():
    return "This is the painel-master page!"

# ===== ENDPOINTS PARA TABELAS DE DADOS =====

@router.get("/dados/pessoas-fisicas", response_class=JSONResponse)
def listar_pessoas_fisicas(db: Session = Depends(get_db)):
    """Lista todas as pessoas físicas para tabela do painel master"""
    pessoas_fisicas = db.query(PessoaFisica).all()
    return [
        {
            "id": pf.id,
            "nome": pf.nome,
            "cpf": pf.cpf,
            "email": pf.email,
            "telefone": pf.telefone,
            "logradouro": pf.logradouro,
            "numero": pf.numero,
            "complemento": pf.complemento,
            "cep": pf.cep,
            "bairro": pf.bairro,
            "municipio": pf.municipio,
            "uf": pf.uf,
            "criado_em": pf.criado_em.strftime("%d/%m/%Y %H:%M") if pf.criado_em else ""
        }
        for pf in pessoas_fisicas
    ]

@router.get("/dados/pessoas-juridicas", response_class=JSONResponse)
def listar_pessoas_juridicas(db: Session = Depends(get_db)):
    """Lista todas as pessoas jurídicas para tabela do painel master"""
    pessoas_juridicas = db.query(PessoaJuridica).all()
    return [
        {
            "id": pj.id,
            "razao_social": pj.razao_social,
            "cnpj": pj.cnpj,
            "nome_fantasia": pj.nome_fantasia,
            "email": pj.email,
            "telefone": pj.telefone,
            "rua": pj.rua,
            "numero": pj.numero,
            "complemento": pj.complemento,
            "bairro": pj.bairro,
            "cep": pj.cep,
            "cidade": pj.cidade,
            "uf": pj.uf,
            "criado_em": pj.criado_em.strftime("%d/%m/%Y %H:%M") if pj.criado_em else ""
        }
        for pj in pessoas_juridicas
    ]

@router.get("/dados/trechos-estadualizacao", response_class=JSONResponse)
def listar_trechos_estadualizacao(db: Session = Depends(get_db)):
    """Lista todos os trechos de estadualização para tabela do painel master"""
    trechos = db.query(TrechoEstadualizacao).all()
    return [
        {
            "id": trecho.id,
            "codigo": trecho.codigo,
            "denominacao": trecho.denominacao,
            "tipo": trecho.tipo,
            "municipio": trecho.municipio,
            "extensao_km": trecho.extensao_km,
            "criado_em": trecho.criado_em.strftime("%d/%m/%Y %H:%M") if trecho.criado_em else ""
        }
        for trecho in trechos
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
def aprovar_usuario_master(usuario_id: int, request: Request, db: Session = Depends(get_db)):
    """Aprovar usuário (apenas master pode fazer)"""
    usuario_master_id = request.session.get("usuario_id")
    
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado"})
    
    usuario.status = "aprovado"
    usuario.ativo = True
    usuario.aprovado_em = date.today()
    usuario.aprovador_id = usuario_master_id
    
    db.commit()
    
    return {"detail": f"Usuário {usuario.nome} aprovado com sucesso"}

@router.post("/acao/reprovar-usuario/{usuario_id}", response_class=JSONResponse)
def reprovar_usuario_master(usuario_id: int, request: Request, db: Session = Depends(get_db)):
    """Reprovar usuário (apenas master pode fazer)"""
    usuario_master_id = request.session.get("usuario_id")
    
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado"})
    
    usuario.status = "reprovado"
    usuario.ativo = False
    usuario.aprovado_em = date.today()
    usuario.aprovador_id = usuario_master_id
    
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

# ===== ENDPOINTS PARA AUDITORIA E EXPORTAÇÃO =====

@router.get("/auditoria/pessoa-fisica/{pf_id}", response_class=JSONResponse)
def obter_auditoria_pessoa_fisica(pf_id: int, db: Session = Depends(get_db)):
    """Obter auditoria de uma pessoa física específica"""
    try:
        # Buscar a pessoa física
        pessoa_fisica = db.query(PessoaFisica).filter(PessoaFisica.id == pf_id).first()
        if not pessoa_fisica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa física não encontrada"})
        
        # Simular dados de auditoria (em produção, isso viria de uma tabela de auditoria)
        auditoria = [
            {
                "id": 1,
                "acao": "Criação",
                "usuario": "Sistema",
                "data": pessoa_fisica.criado_em.strftime("%d/%m/%Y %H:%M") if pessoa_fisica.criado_em else "",
                "detalhes": f"Pessoa física {pessoa_fisica.nome} foi criada no sistema"
            },
            {
                "id": 2,
                "acao": "Visualização",
                "usuario": "Master",
                "data": "16/06/2025 21:30",
                "detalhes": f"Dados da pessoa física {pessoa_fisica.nome} foram visualizados"
            }
        ]
        
        return {
            "pessoa_fisica": {
                "id": pessoa_fisica.id,
                "nome": pessoa_fisica.nome,
                "cpf": pessoa_fisica.cpf
            },
            "auditoria": auditoria
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao buscar auditoria: {str(e)}"})

@router.get("/auditoria/pessoa-juridica/{pj_id}", response_class=JSONResponse)
def obter_auditoria_pessoa_juridica(pj_id: int, db: Session = Depends(get_db)):
    """Obter auditoria de uma pessoa jurídica específica"""
    try:
        # Buscar a pessoa jurídica
        pessoa_juridica = db.query(PessoaJuridica).filter(PessoaJuridica.id == pj_id).first()
        if not pessoa_juridica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa jurídica não encontrada"})
        
        # Simular dados de auditoria (em produção, isso viria de uma tabela de auditoria)
        auditoria = [
            {
                "id": 1,
                "acao": "Criação",
                "usuario": "Sistema",
                "data": pessoa_juridica.criado_em.strftime("%d/%m/%Y %H:%M") if pessoa_juridica.criado_em else "",
                "detalhes": f"Pessoa jurídica {pessoa_juridica.razao_social} foi criada no sistema"
            },
            {
                "id": 2,
                "acao": "Visualização",
                "usuario": "Master",
                "data": "16/06/2025 21:30",
                "detalhes": f"Dados da pessoa jurídica {pessoa_juridica.razao_social} foram visualizados"
            }
        ]
        
        return {
            "pessoa_juridica": {
                "id": pessoa_juridica.id,
                "razao_social": pessoa_juridica.razao_social,
                "cnpj": pessoa_juridica.cnpj
            },
            "auditoria": auditoria
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao buscar auditoria: {str(e)}"})

@router.get("/exportar/pessoa-fisica/{pf_id}/{formato}", response_class=JSONResponse)
def exportar_pessoa_fisica(pf_id: int, formato: str, db: Session = Depends(get_db)):
    """Exportar dados de uma pessoa física em CSV ou Excel"""
    try:
        pessoa_fisica = db.query(PessoaFisica).filter(PessoaFisica.id == pf_id).first()
        if not pessoa_fisica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa física não encontrada"})
        
        # Preparar dados para exportação
        dados = {
            "ID": pessoa_fisica.id,
            "Nome": pessoa_fisica.nome or "",
            "CPF": pessoa_fisica.cpf or "",
            "Email": pessoa_fisica.email or "",
            "Telefone": pessoa_fisica.telefone or "",
            "Logradouro": pessoa_fisica.logradouro or "",
            "Numero": pessoa_fisica.numero or "",
            "Complemento": pessoa_fisica.complemento or "",
            "Bairro": pessoa_fisica.bairro or "",
            "CEP": pessoa_fisica.cep or "",
            "Municipio": pessoa_fisica.municipio or "",
            "UF": pessoa_fisica.uf or "",
            "Criado_em": pessoa_fisica.criado_em.strftime("%d/%m/%Y %H:%M") if pessoa_fisica.criado_em else ""
        }
        
        return {
            "sucesso": True,
            "formato": formato,
            "dados": dados,
            "nome_arquivo": f"pessoa_fisica_{pf_id}_{formato}",            "mensagem": f"Dados da pessoa física {pessoa_fisica.nome} preparados para download em {formato.upper()}"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao exportar: {str(e)}"})

@router.get("/exportar/pessoa-juridica/{pj_id}/{formato}", response_class=JSONResponse)
def exportar_pessoa_juridica(pj_id: int, formato: str, db: Session = Depends(get_db)):
    """Exportar dados de uma pessoa jurídica em CSV ou Excel"""
    try:
        pessoa_juridica = db.query(PessoaJuridica).filter(PessoaJuridica.id == pj_id).first()
        if not pessoa_juridica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa jurídica não encontrada"})
        
        # Preparar dados para exportação
        dados = {
            "ID": pessoa_juridica.id,
            "Razao_Social": pessoa_juridica.razao_social or "",
            "CNPJ": pessoa_juridica.cnpj or "",
            "Nome_Fantasia": pessoa_juridica.nome_fantasia or "",
            "Email": pessoa_juridica.email or "",
            "Telefone": pessoa_juridica.telefone or "",
            "Rua": pessoa_juridica.rua or "",
            "Numero": pessoa_juridica.numero or "",
            "Complemento": pessoa_juridica.complemento or "",
            "Bairro": pessoa_juridica.bairro or "",
            "CEP": pessoa_juridica.cep or "",
            "Cidade": pessoa_juridica.cidade or "",
            "UF": pessoa_juridica.uf or "",
            "Criado_em": pessoa_juridica.criado_em.strftime("%d/%m/%Y %H:%M") if pessoa_juridica.criado_em else ""
        }
        
        return {
            "sucesso": True,
            "formato": formato,
            "dados": dados,
            "nome_arquivo": f"pessoa_juridica_{pj_id}_{formato}",            "mensagem": f"Dados da pessoa jurídica {pessoa_juridica.razao_social} preparados para download em {formato.upper()}"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao exportar: {str(e)}"})

@router.get("/dados/rodovias", response_class=JSONResponse)
def listar_rodovias(db: Session = Depends(get_db)):
    """Lista todas as rodovias para tabela do painel master"""
    rodovias = db.query(RodoviaEstadualizacao).all()
    return [
        {
            "id": rodovia.id,
            "codigo": rodovia.codigo,
            "denominacao": rodovia.denominacao,
            "tipo": rodovia.tipo,
            "municipio": rodovia.municipio,
            "extensao_km": rodovia.extensao_km,
            "criado_em": rodovia.criado_em.strftime("%d/%m/%Y %H:%M") if rodovia.criado_em else ""
        }
        for rodovia in rodovias
    ]

@router.get("/dados/dispositivos", response_class=JSONResponse)
def listar_dispositivos(db: Session = Depends(get_db)):
    """Lista todos os dispositivos para tabela do painel master"""
    dispositivos = db.query(DispositivoEstadualizacao).all()
    return [
        {
            "id": dispositivo.id,
            "codigo": dispositivo.codigo,
            "denominacao": dispositivo.denominacao,
            "tipo": dispositivo.tipo,
            "municipio": dispositivo.municipio,
            "extensao_km": dispositivo.extensao_km,
            "criado_em": dispositivo.criado_em.strftime("%d/%m/%Y %H:%M") if dispositivo.criado_em else ""
        }
        for dispositivo in dispositivos
    ]

@router.get("/dados/obras-arte", response_class=JSONResponse)
def listar_obras_arte(db: Session = Depends(get_db)):
    """Lista todas as obras de arte para tabela do painel master"""
    obras = db.query(ObraArteEstadualizacao).all()
    return [
        {
            "id": obra.id,
            "codigo": obra.codigo,
            "denominacao": obra.denominacao,
            "tipo": obra.tipo,
            "municipio": obra.municipio,
            "extensao_km": obra.extensao_km,
            "criado_em": obra.criado_em.strftime("%d/%m/%Y %H:%M") if obra.criado_em else ""
        }
        for obra in obras
    ]



