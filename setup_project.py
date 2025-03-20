import os

# Caminho base do projeto
base_path = "/workspaces/fad_espacial"

# Caminhos para as pastas
app_path = os.path.join(base_path, "app")
database_path = os.path.join(app_path, "database")
models_path = os.path.join(app_path, "models")

# Caminhos para os arquivos
main_py_path = os.path.join(app_path, "main.py")
models_py_path = os.path.join(models_path, "models.py")
session_py_path = os.path.join(database_path, "session.py")

# Conteúdo dos arquivos __init__.py
init_content = "# Arquivo __init__.py para tornar a pasta um pacote Python\n"

# Conteúdo do main.py
main_py_content = """from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, ArquivoZip
import os

# Configuração do banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria o aplicativo FastAPI
app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os headers
)

# Configuração do Jinja2 para renderizar templates
templates = Jinja2Templates(directory="templates")

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota para servir o frontend (index.html)
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota de upload
@app.post("/validacao/upload/")
async def upload_arquivo(arquivo: UploadFile = File(...)):
    db = SessionLocal()
    try:
        # Verifica se o arquivo é um ZIP
        if not arquivo.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="O arquivo deve ser um ZIP.")

        # Lê o conteúdo do arquivo
        conteudo = await arquivo.read()

        # Salva o arquivo no banco de dados
        arquivo_db = ArquivoZip(nome_arquivo=arquivo.filename, dados=conteudo)
        db.add(arquivo_db)
        db.commit()
        db.refresh(arquivo_db)

        return {"mensagem": "Arquivo importado com sucesso!", "sucesso": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")
    finally:
        db.close()
"""

# Conteúdo do models.py
models_py_content = """from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ArquivoZip(Base):
    __tablename__ = "arquivos_zip"

    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String, index=True)
    dados = Column(LargeBinary)
"""

# Conteúdo do session.py
session_py_content = """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuração do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Cria o engine do banco de dados
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""

# Função para criar arquivos e pastas
def setup_project():
    # Cria os arquivos __init__.py
    for path in [app_path, database_path, models_path]:
        init_file = os.path.join(path, "__init__.py")
        with open(init_file, "w") as f:
            f.write(init_content)
        print(f"Criado: {init_file}")

    # Atualiza main.py
    with open(main_py_path, "w") as f:
        f.write(main_py_content)
    print(f"Atualizado: {main_py_path}")

    # Atualiza models.py
    with open(models_py_path, "w") as f:
        f.write(models_py_content)
    print(f"Atualizado: {models_py_path}")

    # Atualiza session.py
    with open(session_py_path, "w") as f:
        f.write(session_py_content)
    print(f"Atualizado: {session_py_path}")

    print("Projeto configurado com sucesso!")

# Executa a configuração
if __name__ == "__main__":
    setup_project()