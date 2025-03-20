from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.validacao_geometria import router as validacao_router

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configuração do Jinja2
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ Importa os módulos de upload e validação corretamente
app.include_router(upload_router, prefix="/validacao")
app.include_router(validacao_router, prefix="/geometria")
