from fastapi import Request, HTTPException
from app.database.session import SessionLocal
from app.models.cd_usuario import CD_Usuario

def get_usuario_logado(request: Request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        raise HTTPException(status_code=403, detail="Não autenticado.")

    db = SessionLocal()
    usuario = db.query(CD_Usuario).filter(CD_Usuario.id == usuario_id).first()
    db.close()

    if not usuario or not usuario.aprovado:
        raise HTTPException(status_code=403, detail="Usuário inválido ou não aprovado.")
    return usuario
