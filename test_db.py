
from sqlalchemy import create_engine

# String de conexão corrigida
DATABASE_URL = "postgresql://vinicius:Malditas131533*@fad-db.c7cu4eq2gc56.us-east-2.rds.amazonaws.com:5432/postgres?sslmode=require"


# Criar engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("✅ Conexão bem-sucedida ao banco fad-db!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
