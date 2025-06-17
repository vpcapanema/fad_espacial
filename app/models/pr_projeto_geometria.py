from sqlalchemy import Column, Integer, String, DateTime, Text, LargeBinary, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from app.database.base import Base
from datetime import datetime

class TempValidacaoGeometria(Base):
    __tablename__ = "temp_validacao_geometria"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    projeto_temp_id = Column(String, nullable=False)  # UUID temporário
    arquivo_original = Column(String, nullable=False)
    dados_shp = Column(LargeBinary, nullable=True)  # Dados do shapefile
    dados_shx = Column(LargeBinary, nullable=True)
    dados_dbf = Column(LargeBinary, nullable=True) 
    dados_prj = Column(LargeBinary, nullable=True)
    status_validacao = Column(String, default="pendente")
    erros_encontrados = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

class GeometriaValidada(Base):
    __tablename__ = "geometrias_validadas"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    projeto_temp_id = Column(String, nullable=False)
    geom_wkt = Column(Text, nullable=False)  # Geometria em WKT
    srid = Column(Integer, default=4326)
    area_m2 = Column(Float, nullable=True)
    perimetro_m = Column(Float, nullable=True)
    centroide_lat = Column(Float, nullable=True)
    centroide_lon = Column(Float, nullable=True)
    bbox_min_x = Column(Float, nullable=True)
    bbox_min_y = Column(Float, nullable=True)
    bbox_max_x = Column(Float, nullable=True)
    bbox_max_y = Column(Float, nullable=True)
    validado_em = Column(DateTime, default=datetime.utcnow)

class MalhaDer2025(Base):
    __tablename__ = "malha_der_2025"
    __table_args__ = {"schema": "Espacial"}

    id = Column(Integer, primary_key=True, index=True)
    codigo_rodovia = Column(String, nullable=False)
    nome_rodovia = Column(String, nullable=False)
    tipo_rodovia = Column(String, nullable=False)
    geom_wkt = Column(Text, nullable=False)
    extensao_km = Column(Float, nullable=True)
    uf = Column(String, default="SP")
    ativo = Column(Boolean, default=True)
    
class ProjetoFinalizado(Base):
    __tablename__ = "projeto_finalizado"
    __table_args__ = {"schema": "Projetos"}

    id = Column(Integer, primary_key=True, index=True)
    codigo_projeto = Column(String, nullable=False, unique=True)
    tipo_projeto = Column(String, nullable=False)
    interessado_id = Column(Integer, nullable=False)
    representante_id = Column(Integer, nullable=False)
    tipo_elemento_rodoviario = Column(String, nullable=False)
    elemento_rodoviario_id = Column(Integer, nullable=False)
    geometria_validada_id = Column(Integer, nullable=False)
    caminho_croqui = Column(String, nullable=False)
    basemap_selecionado = Column(String, nullable=False)
    zoom_croqui = Column(Integer, nullable=False)
    json_projeto_path = Column(String, nullable=False)
    pdf_relatorio_path = Column(String, nullable=False)
    status = Column(String, default="finalizado")
    criado_em = Column(DateTime, default=datetime.utcnow)
    finalizado_em = Column(DateTime, default=datetime.utcnow)
