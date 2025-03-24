# Script: gerar_modulo_cd.py
# Função: Criar todos os arquivos do módulo de cadastro de PF e PJ para a FAD

import os

# Caminhos base conforme a estrutura do projeto
base_path = "app"
api_path = os.path.join(base_path, "api", "endpoints")
models_path = os.path.join(base_path, "models")
templates_path = os.path.join(base_path, "templates")

# Prefixo do módulo
prefixo = "cd_"

# Arquivos a serem criados
arquivos = {
    os.path.join(api_path, f"{prefixo}cadastro.py"): """from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.templates import templates

router = APIRouter()

@router.get(\"/cadastro\", response_class=HTMLResponse)
async def form_cadastro(request: Request):
    return templates.TemplateResponse(\"cd_cadastro_form.html\", {\"request\": request})

@router.post(\"/cadastro/pf\")
async def cadastrar_pf(
    cpf: str = Form(...),
    nome: str = Form(...),
    email: str = Form(...),
    celular: str = Form(...)
):
    # Validação e persistência virão depois
    if not cpf or not nome or not email or not celular:
        return JSONResponse(content={\"sucesso\": False})
    return JSONResponse(content={\"sucesso\": True})

@router.post(\"/cadastro/pj\")
async def cadastrar_pj(
    cnpj: str = Form(...),
    razao_social: str = Form(...),
    nome_fantasia: str = Form(...),
    rua: str = Form(...),
    numero: str = Form(...),
    complemento: str = Form(...),
    bairro: str = Form(...),
    cep: str = Form(...),
    cidade: str = Form(...),
    uf: str = Form(...)
):
    if not cnpj or not razao_social:
        return JSONResponse(content={\"sucesso\": False})
    return JSONResponse(content={\"sucesso\": True})
""",

    os.path.join(models_path, f"{prefixo}interessado.py"): """from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum
from datetime import datetime

class TipoInteressado(enum.Enum):
    PF = \"PF\"
    PJ = \"PJ\"

class Interessado(Base):
    __tablename__ = \"interessados\"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoInteressado), nullable=False)
    nome = Column(String, nullable=False)
    cpf_cnpj = Column(String, unique=True, nullable=False)
    email = Column(String)
    telefone = Column(String)
    criado_em = Column(DateTime, default=datetime.utcnow)

class RepresentanteLegal(Base):
    __tablename__ = \"representantes_legais\"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    email = Column(String)
    telefone = Column(String)
    id_interessado = Column(Integer, ForeignKey(\"interessados.id\"))
""",

    os.path.join(templates_path, f"{prefixo}cadastro_form.html"): """<!DOCTYPE html>
<html lang=\"pt\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Cadastro de Interessado</title>
    <link rel=\"stylesheet\" href=\"/static/styles.css\">
</head>
<body>
    <div class=\"upload-container\">
        <h2>Cadastro de Pessoa Física</h2>
        <form action=\"/cadastro/pf\" method=\"post\">
            <input type=\"text\" name=\"cpf\" placeholder=\"CPF (apenas números)\" required><br>
            <input type=\"text\" name=\"nome\" placeholder=\"Nome Completo\" required><br>
            <input type=\"email\" name=\"email\" placeholder=\"E-mail\" required><br>
            <input type=\"tel\" name=\"celular\" placeholder=\"Celular com DDD\" required pattern=\"\\(\\d{2}\\) \\d \\d{4}-\\d{4}\"><br>
            <button type=\"submit\">Cadastrar</button>
        </form>
    </div>

    <div class=\"upload-container\">
        <h2>Cadastro de Pessoa Jurídica</h2>
        <form action=\"/cadastro/pj\" method=\"post\">
            <input type=\"text\" name=\"cnpj\" placeholder=\"CNPJ\" required><br>
            <input type=\"text\" name=\"razao_social\" placeholder=\"Razão Social\" required><br>
            <input type=\"text\" name=\"nome_fantasia\" placeholder=\"Nome Fantasia\"><br>
            <input type=\"text\" name=\"rua\" placeholder=\"Rua\"><br>
            <input type=\"text\" name=\"numero\" placeholder=\"Nº\"><br>
            <input type=\"text\" name=\"complemento\" placeholder=\"Complemento\"><br>
            <input type=\"text\" name=\"bairro\" placeholder=\"Bairro\"><br>
            <input type=\"text\" name=\"cep\" placeholder=\"CEP\"><br>
            <input type=\"text\" name=\"cidade\" placeholder=\"Cidade\"><br>
            <input type=\"text\" name=\"uf\" placeholder=\"UF\"><br>
            <button type=\"submit\">Cadastrar</button>
        </form>
    </div>
</body>
</html>
"""
}

# Criar os arquivos
for caminho, conteudo in arquivos.items():
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)

print("✅ Módulo de Cadastro (cd_) gerado com sucesso!")
