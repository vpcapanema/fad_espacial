import geopandas as gpd
import pandas as pd
import os
import zipfile
from shapely import wkb
from sqlalchemy import text
from app.database.session import SessionLocal

def gerar_shapefile_processado():
    session = SessionLocal()

    try:
        # 🔹 Obter interseções da última análise (união de risco e restrição)
        consulta = text("""
            SELECT id, nome, tipo, ST_AsBinary(intersecao) as geom
            FROM (
                SELECT ROW_NUMBER() OVER () as id, nome, 'Risco' as tipo, intersecao FROM conformidade_risco
                UNION ALL
                SELECT ROW_NUMBER() OVER () as id, nome, 'Restrição' as tipo, intersecao FROM conformidade_restricao
            ) as resultado;
        """)
        resultados = session.execute(consulta).fetchall()

        if not resultados:
            # Nenhuma interseção — gera shapefile vazio com schema correto
            df = pd.DataFrame(columns=["id", "nome_area_protegida", "extensao_m", "geometry"])
            gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:31983")
        else:
            dados = []
            for row in resultados:
                geom = wkb.loads(row[3], hex=False)
                extensao = geom.length if geom.geom_type == "LineString" else geom.length
                dados.append({
                    "id": row[0],
                    "nome_area_protegida": row[1],
                    "extensao_m": round(extensao, 2),
                    "geometry": geom
                })
            gdf = gpd.GeoDataFrame(dados, geometry="geometry", crs="EPSG:31983")

        # 🔹 Salvar shapefile temporário
        output_dir = "/tmp/ca_arquivo_processado"
        zip_path = "/tmp/ca_arquivo_processado.zip"

        if os.path.exists(output_dir):
            for f in os.listdir(output_dir):
                os.remove(os.path.join(output_dir, f))
        else:
            os.makedirs(output_dir)

        gdf.to_file(f"{output_dir}/resultado.shp")

        # 🔹 Compactar em .zip
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(output_dir):
                zipf.write(os.path.join(output_dir, file), arcname=file)

        return zip_path

    except Exception as e:
        print("Erro ao gerar shapefile:", e)
        return None

    finally:
        session.close()
