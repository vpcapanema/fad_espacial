from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.session import Base
from datetime import datetime

class CD_Usuario(Base):
    __tablename__ = 'usuarios_sistema'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)
    tipo = Column(String, default='usuario')  # 'master' ou 'usuario'
    aprovado = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
