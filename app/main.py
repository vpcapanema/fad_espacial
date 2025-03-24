from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.jinja import templates
from pathlib import Path
from fastapi.responses import HTMLResponse

# Importações das rotas
from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.validacao_geometria import router as validacao_router
from app.api.endpoints.relatorio import router as relatorio_router
from app.api.endpoints.ca_endpoint import router as conformidade_router
from app.api.endpoints.cd_cadastro import router as cadastro_router  # ✅ NOVO

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Diretórios
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Página inicial (ajuste aqui conforme comportamento desejado)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Rotas registradas
app.include_router(upload_router, prefix="/upload")
app.include_router(validacao_router, prefix="/geometria")
app.include_router(relatorio_router, prefix="/geometria")
app.include_router(conformidade_router, prefix="/conformidade")
app.include_router(cadastro_router)  # Cadastro incluído sem prefixo
