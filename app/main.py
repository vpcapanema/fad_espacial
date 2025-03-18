from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.modulo_validacao import router as validacao_router

app = FastAPI()

# Configurar a pasta de templates para renderizar HTML
templates = Jinja2Templates(directory="app/templates")

# Incluir o módulo de validação na API
app.include_router(validacao_router, prefix="/validacao")

@app.get("/", response_class=HTMLResponse)
def render_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
