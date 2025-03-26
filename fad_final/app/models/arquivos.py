from sqlalchemy import Column, Integer, String, LargeBinary, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ArquivoZip(Base):
    __tablename__ = "arquivos_zip"

    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String, nullable=False)
    dados = Column(LargeBinary, nullable=False)
    data_upload = Column(TIMESTAMP, default=datetime.utcnow)
