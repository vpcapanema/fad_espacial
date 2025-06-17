from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_rodovia_estadualizacao import RodoviaEstadualizacao
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from app.models.cd_obra_arte_estadualizacao import ObraArteEstadualizacao
from app.models.cd_dispositivo_estadualizacao import DispositivoEstadualizacao
from app.schemas.elementos_rodoviarios import RodoviaCreate, TrechoRodoviarioCreate, ObraArteCreate, DispositivoCreate

router = APIRouter()

@router.post("/rodovia/")
def criar_rodovia(rodovia: RodoviaCreate, db: Session = Depends(get_db)):
    nova = RodoviaEstadualizacao(**rodovia.dict())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.post("/trecho-rodoviario/")
def criar_trecho(trecho: TrechoRodoviarioCreate, db: Session = Depends(get_db)):
    novo = TrechoEstadualizacao(**trecho.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.post("/obra-arte/")
def criar_obra(obra: ObraArteCreate, db: Session = Depends(get_db)):
    nova = ObraArteEstadualizacao(**obra.dict())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.post("/dispositivo/")
def criar_dispositivo(dispositivo: DispositivoCreate, db: Session = Depends(get_db)):
    novo = DispositivoEstadualizacao(**dispositivo.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
