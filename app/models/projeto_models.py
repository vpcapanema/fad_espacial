from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from app.database.base import Base
from datetime import datetime

class GeometriaTemporaria(Base):
    __tablename__ = "geometria_temporaria"
    __table_args__ = {"schema": "uploads"}
    
    id = Column(Integer, primary_key=True)
    upload_id = Column(String, unique=True)
    arquivo_original = Column(String)
    geometria_wkt = Column(Text)
    status = Column(String, default="pendente")
    erro_detalhes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

class GeometriaValidada(Base):
    __tablename__ = "geometria_validada" 
    __table_args__ = {"schema": "uploads"}
    
    id = Column(Integer, primary_key=True)
    upload_id = Column(String, unique=True)
    geometria_wkt = Column(Text)
    area_km2 = Column(Float)
    perimetro_km = Column(Float)
    validado_em = Column(DateTime, default=datetime.utcnow)

class Projeto(Base):
    __tablename__ = "projeto"
    __table_args__ = {"schema": "projetos"}
    
    id = Column(Integer, primary_key=True)
    codigo_projeto = Column(String, unique=True)
    tipo_projeto = Column(String)
    interessado_id = Column(Integer)
    representante_id = Column(Integer) 
    elemento_rodoviario_tipo = Column(String)
    elemento_rodoviario_id = Column(Integer)
    upload_id = Column(String)
    croqui_path = Column(String)
    status = Column(String, default="ativo")
    finalizado_em = Column(DateTime)
    json_path = Column(String)
