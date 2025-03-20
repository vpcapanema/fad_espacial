from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.validacao import ValidacaoGeometria

router = APIRouter()

@router.get("/validar/")
def validar_geometria(db: Session = Depends(get_db)):
    # Exemplo de checagem fictícia
    registros = db.query(ValidacaoGeometria).all()

    if not registros:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado.")

    return {"mensagem": "Validação concluída!", "dados": registros}
