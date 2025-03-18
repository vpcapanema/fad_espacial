from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# String de conexão com o RDS atualizado
DATABASE_URL = "postgresql://admin:Malditas131533*@fad-geospatial.c7cu4eq2gc56.us-east-2.rds.amazonaws.com:5432/fad_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
