from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.arquivos import ArquivoZip
import io

router = APIRouter()

# 🔹 Definir a função get_db para evitar erro de importação
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload/")
async def upload_arquivo(arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # ✅ Verifica se o arquivo é um ZIP antes de processar
        if not arquivo.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="O arquivo deve ser um ZIP.")

        # ✅ Lê o conteúdo do arquivo ZIP
        conteudo_zip = await arquivo.read()
        zip_stream = io.BytesIO(conteudo_zip)

        # ✅ Salva o arquivo ZIP no banco de dados
        novo_arquivo = ArquivoZip(
            nome_arquivo=arquivo.filename,
            dados=zip_stream.getvalue()
        )
        db.add(novo_arquivo)
        db.commit()
        db.refresh(novo_arquivo)

        return {"mensagem": "Arquivo importado com sucesso!", "sucesso": True}

    except HTTPException as e:
        raise e  # Re-lança exceções HTTP já tratadas
    except Exception as e:
        db.rollback()  # Desfaz a transação em caso de erro
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar o arquivo: {str(e)}")
