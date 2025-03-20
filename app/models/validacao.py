from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ValidacaoGeometria(Base):
    __tablename__ = "validacao_geometria"

    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String, nullable=False)
    possui_arquivos_obrigatorios = Column(Boolean, nullable=False)
    geometria_valida = Column(Boolean, nullable=False)
    epsg_detectado = Column(Integer)
    epsg_correto = Column(Boolean, nullable=False)
    tipo_geometria = Column(String, nullable=True)
    contagem_feicoes = Column(Integer, nullable=True)
    data_validacao = Column(TIMESTAMP, default=datetime.utcnow)
