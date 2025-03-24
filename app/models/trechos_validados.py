from sqlalchemy import Column, Integer, String, DateTime
from geoalchemy2 import Geometry
from datetime import datetime
from app.database.base import Base


class TrechoValidado(Base):
    __tablename__ = "trechos_validados"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String)
    geometry = Column(Geometry(geometry_type="MULTILINESTRING", srid=4674))
    data_insercao = Column(DateTime, default=datetime.utcnow)
