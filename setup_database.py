import os

# Dados de acesso ao banco de dados
DATABASE_CONFIG = {
    "endpoint": "fad-geospatial.c7cu4eq2gc56.us-east-2.rds.amazonaws.com",
    "porta": 5432,
    "usuario": "postgres",  # Substitua pelo nome do usuário do banco de dados
    "senha": "Malditas131533*",
    "nome_do_banco": "fad_geospatial",  # Substitua pelo nome do banco de dados
}

# Caminho para os arquivos do projeto
BASE_PATH = "/workspaces/fad_espacial"
APP_PATH = os.path.join(BASE_PATH, "app")
DATABASE_PATH = os.path.join(APP_PATH, "database")
MODELS_PATH = os.path.join(APP_PATH, "models")
ENV_FILE = os.path.join(BASE_PATH, ".env")

# Conteúdo do arquivo .env
ENV_CONTENT = f"""
DATABASE_URL=postgresql://{DATABASE_CONFIG['usuario']}:{DATABASE_CONFIG['senha']}@{DATABASE_CONFIG['endpoint']}:{DATABASE_CONFIG['porta']}/{DATABASE_CONFIG['nome_do_banco']}
"""

# Conteúdo do arquivo session.py
SESSION_PY_CONTENT = f"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configuração do banco de dados PostgreSQL
DATABASE_URL = "postgresql://{DATABASE_CONFIG['usuario']}:{DATABASE_CONFIG['senha']}@{DATABASE_CONFIG['endpoint']}:{DATABASE_CONFIG['porta']}/{DATABASE_CONFIG['nome_do_banco']}"

# Cria o engine do banco de dados
engine = create_engine(DATABASE_URL)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()
"""

# Conteúdo do arquivo main.py (apenas a parte relevante)
MAIN_PY_CONTENT = """
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, Base, engine

# Cria o aplicativo FastAPI
app = FastAPI()

# Cria as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exemplo de rota que usa o banco de dados
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute("SELECT 1")
    return {{"message": "Conexão com o banco de dados bem-sucedida!", "data": result.fetchone()}}
"""

# Função para criar/atualizar arquivos
def setup_database():
    # Cria o arquivo .env
    with open(ENV_FILE, "w") as f:
        f.write(ENV_CONTENT.strip())
    print(f"Criado/atualizado: {ENV_FILE}")

    # Cria/atualiza o arquivo session.py
    session_py_path = os.path.join(DATABASE_PATH, "session.py")
    with open(session_py_path, "w") as f:
        f.write(SESSION_PY_CONTENT.strip())
    print(f"Criado/atualizado: {session_py_path}")

    # Atualiza o arquivo main.py
    main_py_path = os.path.join(APP_PATH, "main.py")
    with open(main_py_path, "a") as f:  # Adiciona ao final do arquivo
        f.write("\n" + MAIN_PY_CONTENT.strip())
    print(f"Atualizado: {main_py_path}")

    print("Configuração do banco de dados concluída com sucesso!")

# Executa a configuração
if __name__ == "__main__":
    setup_database()