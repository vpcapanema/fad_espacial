from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Importação das rotas corretamente
from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.validacao_geometria import router as validacao_router
from app.api.endpoints.relatorio import router as relatorio_router
from app.api.endpoints.ca_endpoint import router as conformidade_router



app = FastAPI()

# 🔥 Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 🔥 Servindo arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🔥 Configuração correta do Jinja2Templates
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 🔥 Verificar se a pasta templates existe
if not TEMPLATES_DIR.exists():
    print(f"⚠️  A pasta de templates não foi encontrada em {TEMPLATES_DIR}")

# ✅ Rota para servir o index.html corretamente
@app.get("/", response_class=Jinja2Templates.TemplateResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ Incluindo as rotas corretamente
app.include_router(upload_router, prefix="/upload")
app.include_router(validacao_router, prefix="/geometria")
app.include_router(relatorio_router, prefix="/geometria")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(conformidade_router, prefix="/conformidade")



