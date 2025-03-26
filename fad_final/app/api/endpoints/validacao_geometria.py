from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, FileResponse
from app.database.session import get_db
from app.models.geometrias import Geometria
from app.models.trechos_validados import TrechoValidado
from app.models.validacao import ValidacaoGeometria
from geoalchemy2.shape import to_shape
from geoalchemy2 import WKTElement
from datetime import datetime
from app.relatorios.relatorio_validacao import gerar_relatorio_validacao
import geopandas as gpd
import os

router = APIRouter()

@router.get("/validar")
def validar_geometria(db: Session = Depends(get_db)):
    try:
        geometrias = db.query(Geometria).all()
        if not geometrias:
            raise HTTPException(status_code=404, detail="Nenhuma geometria encontrada para validar.")

        features = []
        for g in geometrias:
            geom = to_shape(g.geometria)
            features.append({"Cod": g.nome, "geometry": geom})
        gdf = gpd.GeoDataFrame(features, geometry="geometry", crs="EPSG:4674")

        relatorio = []

        # 1. Presença da coluna Cod
        cond1 = "Cod" in gdf.columns
        relatorio.append(("Presença da coluna 'Cod'", cond1))

        # 2. Cod não pode ser nulo ou em branco
        cond2 = not gdf["Cod"].isnull().any() and not (gdf["Cod"].astype(str).str.strip() == "").any() if cond1 else False
        relatorio.append(("Campo 'Cod' não está em branco ou nulo", cond2))

        # 3. Geometria nula
        cond3 = not gdf["geometry"].isnull().any()
        relatorio.append(("Geometria não é nula", cond3))

        # 4. Dentro do estado de SP
        sp_bbox = [-53.1103, -25.439, -44.1728, -19.7848]
        gdf["centroid"] = gdf.geometry.centroid
        cond4 = gdf["centroid"].apply(lambda p: sp_bbox[0] <= p.x <= sp_bbox[2] and sp_bbox[1] <= p.y <= sp_bbox[3]).all()
        relatorio.append(("Dentro do limite do Estado de SP", cond4))

        validado = all([c[1] for c in relatorio])
        epsg_detectado = 4674
        tipo_geometria = gdf.geometry.type.mode().iloc[0]
        contagem_feicoes = len(gdf)

        validacao = ValidacaoGeometria(
            nome_arquivo=geometrias[0].nome,
            possui_arquivos_obrigatorios=True,
            geometria_valida=validado,
            epsg_detectado=epsg_detectado,
            epsg_correto=True,
            tipo_geometria=tipo_geometria,
            contagem_feicoes=contagem_feicoes,
            data_validacao=datetime.utcnow()
        )
        db.add(validacao)
        db.commit()

        gerar_relatorio_validacao(
            nome_arquivo=validacao.nome_arquivo,
            criterios=relatorio,
            caminho_destino="/tmp/relatorio_validacao.pdf",
            epsg_detectado=epsg_detectado,
            tipo_geometria=tipo_geometria,
            contagem_feicoes=contagem_feicoes
        )

        if validado:
            for _, row in gdf.iterrows():
                geom = WKTElement(row.geometry.wkt, srid=4674)
                db.add(TrechoValidado(codigo=str(row["Cod"]), geometry=geom))
        db.query(Geometria).delete()
        db.commit()

        return JSONResponse(content={
            "validado": validado,
            "mensagem": "Geometria validada com sucesso!" if validado else "A geometria contém erros.",
            "relatorio_gerado": True
        })

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao validar geometria: {str(e)}")

@router.get("/relatorio")
def baixar_relatorio_validacao():
    caminho = "/tmp/relatorio_validacao.pdf"
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
    return FileResponse(caminho, filename="relatorio_validacao.pdf", media_type="application/pdf")
