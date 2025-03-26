import os
import pdfkit
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import text
from app.database.session import SessionLocal

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../templates")

def gerar_relatorio_processamento():
    session = SessionLocal()

    try:
        trecho = session.execute(text("""
            SELECT nome_arquivo, municipio, trecho_nome, data_validacao
            FROM validacao_geometria
            WHERE validado = TRUE
            ORDER BY data_validacao DESC
            LIMIT 1;
        """)).fetchone()

        if not trecho:
            raise Exception("Trecho validado não encontrado.")

        nome_arquivo, municipio, trecho_nome, data = trecho

        camadas = session.execute(text("""
            SELECT DISTINCT tipo FROM (
                SELECT 'Risco' AS tipo FROM conformidade_risco
                UNION
                SELECT 'Restrição' AS tipo FROM conformidade_restricao
            ) AS combinadas;
        """)).fetchall()

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("ca_processamento_template.html")

        html = template.render(
            nome_arquivo=nome_arquivo,
            municipio=municipio,
            trecho_nome=trecho_nome,
            data=data.strftime("%d/%m/%Y"),
            camadas=[c[0] for c in camadas],
            srid="EPSG:31983",
            buffer_km="10 km (zona de amortecimento)",
            horario=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )

        output_path = "/tmp/ca_relatorio_processamento.pdf"
        pdfkit.from_string(html, output_path)

        return output_path

    except Exception as e:
        print("Erro ao gerar relatório de processamento:", e)
        return None

    finally:
        session.close()
