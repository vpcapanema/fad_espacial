import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import text
from app.database.session import SessionLocal
from datetime import datetime

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../templates")

def gerar_laudo_sintetico():
    session = SessionLocal()
    try:
        trecho = session.execute(text("""
            SELECT municipio, trecho_nome, numero_sei, solicitante, diretoria_regional,
                   conserva, data_validacao
            FROM validacao_geometria
            WHERE validado = TRUE
            ORDER BY data_validacao DESC
            LIMIT 1
        """)).fetchone()

        if not trecho:
            raise Exception("Nenhum trecho validado encontrado.")

        municipio, via, numero_sei, solicitante, diretoria, conserva, data = trecho

        risco = session.execute(text("SELECT nome FROM conformidade_risco")).fetchall()
        restricao = session.execute(text("SELECT nome FROM conformidade_restricao")).fetchall()

        nomes = list({r[0] for r in risco + restricao})

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("ca_laudo_sintetico_template.html")

        html = template.render(
            numero_sei=numero_sei or "___________",
            solicitante=solicitante or "___________",
            municipio=municipio,
            diretoria=diretoria or "___________",
            conserva=conserva or "___________",
            via=via,
            data=data.strftime("%d/%m/%Y"),
            intersecoes=nomes,
            horario=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )

        output_path = "/tmp/ca_laudo_sintetico_conformidade_ambiental.pdf"
        pdfkit.from_string(html, output_path)
        return output_path

    except Exception as e:
        print("Erro ao gerar laudo sintético:", e)
        return None

    finally:
        session.close()
