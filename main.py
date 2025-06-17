from app.api.endpoints import cd_consultas_auxiliares
from app.api.endpoints import pr_debug_log_projeto
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.core.session_control import FADSessionMiddleware, session_router # MODIFICADO: session_router importado
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
from pathlib import Path
import os
import threading
import webbrowser
import requests
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_usuario_sistema import UsuarioSistema
from app.models.cd_pessoa_fisica import PessoaFisica
from app.models.cd_pessoa_juridica import PessoaJuridica
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from datetime import datetime, timedelta
from starlette.responses import RedirectResponse

# ================================ 📦 Importações de módulos ================================
from app.api.endpoints.au_autenticacao import router as autenticacao_router
from app.api.endpoints.ca_endpoint import router as conformidade_ambiental_router
from app.api.endpoints.cd_aprovar_usuario import router as aprovar_usuario_router
from app.api.endpoints.cd_cadastro_pessoa_fisica import router as cadastro_pf_router
from app.api.endpoints.cd_cadastro_pessoa_juridica import router as cadastro_pj_router
from app.api.endpoints.cd_cadastro_trechos_estadualizacao import router as cadastro_trechos_router
from app.api.endpoints.cd_cadastro_usuario_sistema import router as cadastro_usuario_router
# Novos endpoints separados para elementos rodoviários
from app.api.endpoints.cd_cadastro_trecho_rodoviario import router as cadastro_trecho_rodoviario_router
from app.api.endpoints.cd_cadastro_rodovia import router as cadastro_rodovia_router
from app.api.endpoints.cd_cadastro_dispositivo import router as cadastro_dispositivo_router
from app.api.endpoints.cd_cadastro_obra_arte import router as cadastro_obra_arte_router
from app.api.endpoints.pn_menu_navegacao import router as menu_navegacao_router
from app.api.endpoints.pn_painel_usuario_administrador import router as painel_administrador_router
from app.api.endpoints.pn_painel_usuario_comum import router as painel_usuario_comum_router
from app.api.endpoints.pn_painel_usuario_master import router as painel_master_router
from app.api.endpoints.pn_auditoria_exportacao import router as auditoria_exportacao_router
from app.api.endpoints.vw_painel_master_projetos import router as painel_master_projetos_router
from app.api.endpoints.pr_gravar_projeto import router as cadastrar_projeto_router
from app.api.endpoints.pr_relatorio_upload import router as relatorio_upload_router
from app.api.endpoints.pr_relatorio_validacao import router as relatorio_validacao_router
from app.api.endpoints.pr_salvar_geometria_validada import router as salvar_geometria_router
from app.api.endpoints.pr_projeto_api import router as projeto_api_router
from app.api.endpoints.download_teste import router as download_teste_router
from app.api.endpoints.projeto_novo import router as projeto_novo_router
from app.api.endpoints.pr_status_projeto import router as status_projeto_router
from app.api.endpoints.pr_upload_zip import router as upload_router
from app.api.endpoints.pr_validacao_geometria import router as validacao_geometria_router
from app.api.endpoints.vw_painel_administrador import router as vw_painel_administrador_router
from app.api.endpoints.vw_projetos_usuario_comum import router as vw_projetos_usuario_comum_router
from app.api.endpoints.pr_fluxo_modular import router as fluxo_modular_router
from app.api.endpoints.pr_modulos_pages import router as modulos_pages_router
from app.api.endpoints.au_recuperacao_senha import router as recuperacao_senha_router
from app.api.endpoints.pr_modulos_management import router as modulos_management_router
from app.api.endpoints.mapa_rotas import router as mapa_rotas_router
from app.api.endpoints.pr_mock_projeto import router as mock_projeto_router
from app.api.endpoints.mock_shapes import router as mock_shapes_router
from app.api.endpoints.cadastro_elemetos_rodoviarios import endpoints as cadastro_elementos_router

# ============================ 🚀 Instância principal da API ============================
app = FastAPI(
    title="FAD - Ferramenta de Análise Dinamizada",
    description="Plataforma para análise técnica e ambiental de dados geoespaciais",
    version="1.0.0"
)

# ============================= 🔐 Sistema de Controle de Sessão =============================

# Middleware de sessão básico
app.add_middleware(SessionMiddleware, secret_key="CHAVE_SECRETA_SUPER_FAD_2025", same_site="lax")

# Middleware de controle de sessão avançado
app.add_middleware(FADSessionMiddleware)

# ============================ 🌐 Middleware de CORS ============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ============================ 📝 Middleware de Logging ============================
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        method = request.method
        url = str(request.url)
        headers = dict(request.headers)
        try:
            body = await request.body()
            body_str = body.decode('utf-8') if body else ''
        except Exception:
            body_str = '<não foi possível ler o corpo>'
        print(f"\n[REQUISIÇÃO] {method} {url}")
        print(f"Headers: {headers}")
        if body_str and 'application/json' in headers.get('content-type', ''):
            print(f"Payload: {body_str}")
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        print(f"[RESPOSTA] Status: {response.status_code} | Tempo: {process_time:.2f}ms")
        # Não printar HTML nem corpo de resposta
        print("-"*60)
        return response

app.add_middleware(LoggingMiddleware)

# ============================ 🔒 Middleware de Proteção de Rotas ============================

class RouteProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para proteger rotas específicas baseado em autenticação e permissões
    """
    
    # Rotas que requerem autenticação
    PROTECTED_ROUTES = {
        "/painel-master": ["master"],           # Apenas usuários master
        "/painel-coordenador": ["coordenador", "master"],  # Coordenadores e master
        "/painel-analista": ["analista", "coordenador", "master"],  # Analistas e superiores
        "/cadastro": ["analista", "coordenador", "master"],  # Qualquer usuário logado
        "/upload": ["analista", "coordenador", "master"],    # Qualquer usuário logado
        "/relatorio": ["analista", "coordenador", "master"], # Qualquer usuário logado
        "/validacao": ["coordenador", "master"],              # Apenas coordenadores e master
        "/aprovar": ["master"],                               # Apenas master
    }
    
    # Rotas públicas (não precisam de autenticação)
    PUBLIC_ROUTES = [
        "/",
        "/login",
        "/cadastro-usuario",
        "/recuperacao",
        "/static",
        "/docs",
        "/openapi.json",
        "/redoc"
    ]
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Verificar se é uma rota pública
        if any(path.startswith(public_route) for public_route in self.PUBLIC_ROUTES):
            return await call_next(request)
        
        # Verificar se é uma rota protegida
        protected_route = None
        required_roles = None
        
        for route_prefix, roles in self.PROTECTED_ROUTES.items():
            if path.startswith(route_prefix):
                protected_route = route_prefix
                required_roles = roles
                break
        
        # Se não é uma rota protegida, permitir acesso
        if not protected_route:
            return await call_next(request)
        
        # Verificar se o usuário está autenticado
        usuario_id = request.session.get("usuario_id")
        usuario_tipo = request.session.get("usuario_tipo")
        
        if not usuario_id or not usuario_tipo:
            # Usuário não autenticado - redirecionar para login
            if request.headers.get("accept", "").startswith("application/json"):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Acesso negado. Faça login para continuar."}
                )
            else:
                return RedirectResponse(url="/login", status_code=302)
        
        # Verificar se o usuário tem permissão para acessar a rota
        if usuario_tipo not in required_roles:
            # Usuário autenticado mas sem permissão
            if request.headers.get("accept", "").startswith("application/json"):
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": f"Acesso negado. Seu tipo de usuário ({usuario_tipo}) não tem permissão para acessar {protected_route}. Tipos permitidos: {', '.join(required_roles)}"
                    }
                )
            else:
                return RedirectResponse(url="/login", status_code=302)
        
        # Usuário autenticado e com permissão - permitir acesso
        return await call_next(request)

# Adicionar middleware de proteção de rotas
app.add_middleware(RouteProtectionMiddleware)

# ======================== 📁 Diretórios do Projeto ========================
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

os.makedirs(STATIC_DIR / "images", exist_ok=True)
os.makedirs(STATIC_DIR / "relatorios", exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# =================== 🏠 Página Inicial ===================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "static_url": "/static/images"
    })

# ✅ Nova rota limpa para exibir o login
@app.get("/login", response_class=HTMLResponse)
def tela_login(request: Request):
    return templates.TemplateResponse("au_login.html", {"request": request})

# ADICIONADO:
@app.get("/boas-vindas", response_class=HTMLResponse)
async def boas_vindas_page(request: Request):
    context = {"request": request}
    # Se você precisar passar dados específicos para a página de boas-vindas,
    # como informações do usuário logado, você pode adicioná-los ao 'context'.
    # Exemplo: if "usuario_nome" in request.session:
    # context["usuario_nome"] = request.session["usuario_nome"]
    return templates.TemplateResponse("boas_vindas.html", context)

# ✅ Rota para o mapa de rotas
@app.get("/mapa-rotas", response_class=HTMLResponse)
def mapa_rotas(request: Request):
    return templates.TemplateResponse("mapa_rotas_fad_atualizado.html", {"request": request})
# Rota para exibir o formulário de envio de cadastro de usuário (Backend)
@app.get("/cadastro-usuario-sistema-envio", response_class=HTMLResponse)
def view_cadastro_usuario_envio(request: Request):
    return templates.TemplateResponse("cd_cadastro_usuario_envio.html", {"request": request})

# =============== 🐞 Rota Debug ===============
@app.get("/debug", response_class=JSONResponse)
async def debug_info(request: Request):
    return {
        "status": "online",
        "base_url": str(request.base_url),
        "static_files_path": str(STATIC_DIR),
        "available_images": os.listdir(STATIC_DIR / "images") if os.path.exists(STATIC_DIR / "images") else []
    }

# =============== 🖼️ Favicon ===============
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    path = STATIC_DIR / "images/favicon.ico"
    if path.exists():
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"detail": "Favicon não encontrado."})

# =============== 🖼️ Teste de Logo ===============
@app.get("/test-logo", include_in_schema=False)
async def test_logo():
    path = STATIC_DIR / "images/fad_logo_banco_completo1.png"
    if path.exists():
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"detail": "Logo não encontrado."})

# ==================== 🔌 INCLUSÃO DE ROTAS API ====================
# ⚠️  ATENÇÃO: SEÇÃO PROTEGIDA - NÃO MODIFICAR AS ROTAS VALIDADAS ⚠️
# 
# Esta seção contém rotas já testadas e validadas em produção.
# QUALQUER ALTERAÇÃO deve ser feita com extremo cuidado e apenas
# após backup completo do sistema.
#
# Data da última validação: 17/06/2025
# Responsável: Sistema de Auditoria FAD
# ========================================================================

# 🔐 === ROTAS VALIDADAS E PROTEGIDAS - NÃO ALTERAR === 🔐
# As rotas abaixo foram testadas e estão funcionando corretamente.
# Modificações podem quebrar funcionalidades críticas do sistema.

# 📋 SEÇÃO 1: AUTENTICAÇÃO E CONTROLE DE ACESSO (VALIDADO ✅)
app.include_router(autenticacao_router)                                    # ✅ VALIDADO 17/06/2025
app.include_router(aprovar_usuario_router)                                 # ✅ VALIDADO 17/06/2025
app.include_router(session_router)                                         # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 2: PAINÉIS DE USUÁRIO (VALIDADO ✅)
app.include_router(painel_master_router, prefix="/painel-master")          # ✅ VALIDADO 17/06/2025 - CRÍTICO
app.include_router(auditoria_exportacao_router, prefix="/painel-master")   # ✅ VALIDADO 17/06/2025 - CRÍTICO
app.include_router(painel_administrador_router, prefix="/painel-coordenador")  # ✅ VALIDADO 17/06/2025
app.include_router(painel_usuario_comum_router, prefix="/painel-analista")     # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 3: CADASTROS BÁSICOS (VALIDADO ✅)
app.include_router(cadastro_usuario_router)                                # ✅ VALIDADO 17/06/2025
app.include_router(cadastro_pf_router)                                     # ✅ VALIDADO 17/06/2025
app.include_router(cadastro_pj_router)                                     # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 4: ELEMENTOS RODOVIÁRIOS (VALIDADO ✅)
app.include_router(cadastro_trechos_router)                                # ✅ VALIDADO 17/06/2025
app.include_router(cadastro_trecho_rodoviario_router)                      # ✅ VALIDADO 17/06/2025
app.include_router(cadastro_rodovia_router)                                # ✅ VALIDADO 17/06/2025
app.include_router(cadastro_dispositivo_router)                           # ✅ VALIDADO 17/06/2025
app.include_router(cadastro_obra_arte_router)                             # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 5: NAVEGAÇÃO E MENU (VALIDADO ✅)
app.include_router(menu_navegacao_router)                                  # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 6: PROJETOS E RELATÓRIOS (VALIDADO ✅)
app.include_router(cadastrar_projeto_router)                              # ✅ VALIDADO 17/06/2025
app.include_router(painel_master_projetos_router)                         # ✅ VALIDADO 17/06/2025
app.include_router(relatorio_upload_router)                               # ✅ VALIDADO 17/06/2025
app.include_router(relatorio_validacao_router)                            # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 7: UPLOADS E GEOMETRIAS (VALIDADO ✅)
app.include_router(upload_router)                                          # ✅ VALIDADO 17/06/2025
app.include_router(salvar_geometria_router)                               # ✅ VALIDADO 17/06/2025
app.include_router(projeto_api_router)                                      # ✅ VALIDADO 17/06/2025
app.include_router(projeto_novo_router)                                     # ✅ NOVO FLUXO 17/06/2025
app.include_router(validacao_geometria_router)                           # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 8: VIEWS E PAINÉIS ADMINISTRATIVOS (VALIDADO ✅)
app.include_router(vw_painel_administrador_router)                        # ✅ VALIDADO 17/06/2025
app.include_router(vw_projetos_usuario_comum_router)                      # ✅ VALIDADO 17/06/2025
app.include_router(status_projeto_router)                                 # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 9: MÓDULOS E FLUXOS (VALIDADO ✅)
app.include_router(fluxo_modular_router)                                   # ✅ VALIDADO 17/06/2025
app.include_router(modulos_pages_router)                                   # ✅ VALIDADO 17/06/2025

# 📋 SEÇÃO 10: CONFORMIDADE AMBIENTAL (VALIDADO ✅)
app.include_router(conformidade_ambiental_router)                          # ✅ VALIDADO 17/06/2025

# 🔐 === FIM DAS ROTAS PROTEGIDAS === 🔐

# ========================================================================
# 📍 SEÇÃO 11: ROTAS ADICIONAIS E UTILITÁRIOS (NÃO CRÍTICAS)
# ========================================================================
# Rotas que podem ser modificadas sem afetar funcionalidades críticas

app.include_router(mapa_rotas_router)                                      # 🗺️ Mapa de rotas visual
app.include_router(recuperacao_senha_router)                               # 🔑 Recuperação de senha
app.include_router(modulos_management_router)                              # 🔧 Gerenciamento de módulos  
app.include_router(mock_projeto_router)                                    # 🧪 Mock de projetos
app.include_router(mock_shapes_router)                                     # 🧪 Mock de shapes
# app.include_router(cadastro_elementos_router)                              # 📝 Cadastro de elementos - TEMPORARIAMENTE DESABILITADO

# ========================================================================
# ⚠️  IMPORTANTE: 
# - Todas as rotas acima foram testadas em 17/06/2025
# - Sistema de auditoria e exportação funcionando 100%
# - Painéis Master, Coordenador e Analista operacionais
# - NÃO REMOVER, ALTERAR OU REORDENAR sem documentação adequada
# ========================================================================

# ============================ 🚀 Inicialização do Servidor (Opcional) ============================
