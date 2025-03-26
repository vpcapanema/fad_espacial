from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.session import Base

# Pessoa Física
class InteressadoPF(Base):
    __tablename__ = "interessados_pf"
    __table_args__ = {"schema": "cadastro_interessados"}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

# Pessoa Jurídica
class InteressadoPJ(Base):
    __tablename__ = "interessados_pj"
    __table_args__ = {"schema": "cadastro_interessados"}

    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
    nome_fantasia = Column(String)
    email = Column(String)
    telefone = Column(String)
    rua = Column(String)
    numero = Column(String)
    complemento = Column(String)
    bairro = Column(String)
    cep = Column(String)
    cidade = Column(String)
    uf = Column(String)
    criado_em = Column(DateTime, default=datetime.utcnow)

# Trecho
class InteressadoTrecho(Base):
    __tablename__ = "interessados_trechos"
    __table_args__ = {"schema": "cadastro_interessados"}

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, nullable=False)
    denominacao = Column(String, nullable=False)
    municipio = Column(String, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
