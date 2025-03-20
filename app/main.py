from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 🔥 Importando as rotas corretamente
from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.validacao_geometria import router as validacao_router

app = FastAPI()

# 🔥 Configuração correta do CORS para permitir chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 Agora permite chamadas de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # 🔥 Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # 🔥 Permite qualquer cabeçalho
    expose_headers=["*"],  # 🔥 Garante que os headers sejam expostos corretamente
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configuração do Jinja2
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ Incluindo as rotas corretamente
app.include_router(upload_router, prefix="/upload")
app.include_router(validacao_router, prefix="/geometria")
