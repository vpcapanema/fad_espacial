from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum
from datetime import datetime

class TipoInteressado(enum.Enum):
    PF = "PF"
    PJ = "PJ"

class Interessado(Base):
    __tablename__ = "interessados"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoInteressado), nullable=False)
    nome = Column(String, nullable=False)
    cpf_cnpj = Column(String, unique=True, nullable=False)
    email = Column(String)
    telefone = Column(String)
    criado_em = Column(DateTime, default=datetime.utcnow)

class RepresentanteLegal(Base):
    __tablename__ = "representantes_legais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    email = Column(String)
    telefone = Column(String)
    id_interessado = Column(Integer, ForeignKey("interessados.id"))
