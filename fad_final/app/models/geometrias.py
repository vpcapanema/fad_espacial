from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Geometria(Base):
    __tablename__ = "geometrias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)  # Nome do arquivo ou identificador
    geometria = Column(Geometry(geometry_type="GEOMETRY", srid=4674), nullable=False)
