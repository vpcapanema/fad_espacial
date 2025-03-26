from sqlalchemy import text
from app.database.session import SessionLocal

def processar_conformidade(payload: dict) -> dict:
    session = SessionLocal()
    try:
        # Verifica se existe uma geometria validada
        validado = session.execute(text("""
            SELECT COUNT(*) FROM validacao_geometria WHERE geometria_valida = TRUE

        """)).scalar()

        if validado == 0:
            return {"sucesso": False, "erro": "Nenhuma geometria validada encontrada."}

        # Consulta as views para verificar resultado do cruzamento
        risco = session.execute(text("SELECT COUNT(*) FROM conformidade_risco")).scalar()
        restricao = session.execute(text("SELECT COUNT(*) FROM conformidade_restricao")).scalar()

        return {
            "sucesso": True,
            "mensagem": f"Análise de conformidade realizada com sucesso. {risco} interseções de risco e {restricao} de restrição foram detectadas.",
        }

    except Exception as e:
        print("Erro no processamento da conformidade:", e)
        return {"sucesso": False, "erro": str(e)}

    finally:
        session.close()
