from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://vinicius:Malditas131533*@fad-db.c7cu4eq2gc56.us-east-2.rds.amazonaws.com:5432/fad_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Função utilitária de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
