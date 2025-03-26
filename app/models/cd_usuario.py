from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.session import Base
from datetime import datetime

class CD_Usuario(Base):
    __tablename__ = 'usuarios_sistema'
    __table_args__ = {'schema': 'usuarios_sistema'}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False, index=True)  # NOVO
    email = Column(String, nullable=False)
    senha_hash = Column(String, nullable=False)
    tipo = Column(String, default='usuario')
    aprovado = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
