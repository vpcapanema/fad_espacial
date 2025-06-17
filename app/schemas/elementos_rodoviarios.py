from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Pydantic models para validação dos dados de entrada

class RodoviaCreate(BaseModel):
    codigo: str = Field(...)
    denominacao: str = Field(...)
    tipo: str = Field(...)
    municipio: str = Field(...)
    extensao_km: float = Field(...)
    criado_em: Optional[datetime] = None

class TrechoRodoviarioCreate(BaseModel):
    codigo: str = Field(...)
    denominacao: str = Field(...)
    tipo: str = Field(...)
    municipio: str = Field(...)
    extensao_km: float = Field(...)
    criado_em: Optional[datetime] = None

class ObraArteCreate(BaseModel):
    codigo: str = Field(...)
    denominacao: str = Field(...)
    tipo: str = Field(...)
    municipio: str = Field(...)
    extensao_km: float = Field(...)
    criado_em: Optional[datetime] = None

class DispositivoCreate(BaseModel):
    codigo: str = Field(...)
    denominacao: str = Field(...)
    tipo: str = Field(...)
    municipio: str = Field(...)
    extensao_km: float = Field(...)
    criado_em: Optional[datetime] = None
