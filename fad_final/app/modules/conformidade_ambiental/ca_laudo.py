import os
import pdfkit
import base64
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import text
from app.database.session import SessionLocal
import matplotlib.pyplot as plt
from shapely import wkb
from shapely.geometry import LineString
import io

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../templates")

def gerar_relatorio_pdf():
    session = SessionLocal()
    try:
        # 🔹 Obter trecho validado
        trecho = session.execute(text("""
            SELECT municipio, trecho_nome, numero_sei, solicitante, diretoria_regional,
                   conserva, ST_AsText(ST_Transform(geom, 4326)) as geom4326,
                   data_validacao
            FROM validacao_geometria
            WHERE validado = TRUE
            ORDER BY data_validacao DESC
            LIMIT 1
        """)).fetchone()

        if not trecho:
            raise Exception("Nenhum trecho validado encontrado.")

        municipio, via, numero_sei, solicitante, diretoria, conserva, wkt_geom, data = trecho

        # 🔹 Extrair coordenadas do WKT
        geom = LineString(eval(wkt_geom.replace("LINESTRING", "").strip()))
        coordenadas = [{"lon": f"{lon:.8f}", "lat": f"{lat:.8f}"} for lon, lat in geom.coords]

        # 🔹 Obter listas de risco e restrição
        risco = session.execute(text("SELECT nome FROM conformidade_risco")).fetchall()
        restricao = session.execute(text("SELECT nome FROM conformidade_restricao")).fetchall()
        risco = [r[0] for r in risco]
        restricao = [r[0] for r in restricao]

        # 🔹 Gerar imagem do mapa
        fig, ax = plt.subplots(figsize=(8, 6))
        x, y = zip(*geom.coords)
        ax.plot(x, y, color='blue', linewidth=3)
        ax.set_title("Mapa de Situação", fontsize=14)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True)

        # 🔹 Converter imagem para base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        mapa_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        # 🔹 Definir conclusão automática
        if not risco and not restricao:
            conclusao = "A rodovia em questão não apresenta risco ou restrição ambiental, pois não intersecta nenhuma das áreas protegidas e suas respectivas zonas de amortecimento avaliadas."
        else:
            conclusao = "A rodovia em questão apresenta sobreposição com áreas protegidas ou suas zonas de amortecimento, conforme detalhado neste laudo."

        # 🔹 Renderizar HTML com Jinja2
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("relatorio_conformidade.html")
        html = template.render(
            numero_sei=numero_sei or "___________",
            solicitante=solicitante or "___________",
            municipio=municipio,
            diretoria=diretoria or "___________",
            conserva=conserva or "___________",
            via=via,
            data=data.strftime("%d/%m/%Y"),
            coordenadas=coordenadas,
            risco=risco,
            restricao=restricao,
            mapa_base64=mapa_base64,
            conclusao=conclusao
        )

        # 🔹 Gerar PDF
        output_path = "/tmp/laudo_conformidade.pdf"
        pdfkit.from_string(html, output_path)
        return output_path

    except Exception as e:
        print("Erro ao gerar laudo:", str(e))
        return None

    finally:
        session.close()
