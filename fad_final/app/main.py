from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import os

# Importações das rotas
from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.validacao_geometria import router as validacao_router
from app.api.endpoints.relatorio import router as relatorio_router
from app.api.endpoints.ca_endpoint import router as conformidade_router
from app.api.endpoints.cd_cadastro import router as cadastro_router
from app.api.endpoints.cd_autenticacao import router as cd_autenticacao_router  # ✅ mantido apenas este

# Inicialização do app FastAPI
app = FastAPI(
    title="FAD - Ferramenta de Análise Dinamizada",
    description="Plataforma para análise técnica e ambiental de dados geoespaciais",
    version="1.0.0"
)

# ✅ Adicionando middleware de sessão segura
app.add_middleware(SessionMiddleware, secret_key="CHAVE_SECRETA_SUPER_FAD_2025")

# Configuração do CORS para Codespaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configuração de diretórios
BASE_DIR = Path(__file__).parent.parent
APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"

# Configuração dos templates Jinja2
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Verifica e cria diretórios estáticos se não existirem
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(STATIC_DIR / "images", exist_ok=True)

# Montagem da pasta estática
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Página principal
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "static_url": "/static/images"
    })

# Rota para verificação do ambiente
@app.get("/debug", response_class=JSONResponse)
async def debug_info(request: Request):
    return {
        "status": "online",
        "base_url": str(request.base_url),
        "static_files_path": str(STATIC_DIR),
        "available_images": os.listdir(STATIC_DIR / "images") if os.path.exists(STATIC_DIR / "images") else []
    }

# Rotas da API
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(validacao_router, prefix="/api/geometria", tags=["Validação"])
app.include_router(relatorio_router, prefix="/api/relatorios", tags=["Relatórios"])
app.include_router(conformidade_router, prefix="/api/conformidade", tags=["Conformidade Ambiental"])
app.include_router(cadastro_router)  # ✅ agora acessível diretamente em /cadastro
app.include_router(cd_autenticacao_router)

# Rota para favicon com fallback se não existir
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    path = STATIC_DIR / "images/favicon.ico"
    if path.exists():
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"detail": "Favicon não encontrado."})
