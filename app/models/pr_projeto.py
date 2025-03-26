from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database.session import Base

class Projeto(Base):
    __tablename__ = "projetos"
    __table_args__ = {"schema": "cadastro_interessados"}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    interessado_id = Column(Integer, ForeignKey("cadastro_interessados.interessados_pj.id"))
    representante_id = Column(Integer, ForeignKey("cadastro_interessados.interessados_pf.id"))
    trecho_id = Column(Integer, ForeignKey("cadastro_interessados.interessados_trechos.id"))
    modulos_selecionados = Column(String, nullable=False)  # pode ser JSONB, se desejar
    criado_em = Column(DateTime, default=datetime.utcnow)
