from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.arquivos import ArquivoZip
from app.models.validacao import ValidacaoGeometria
from app.models.trechos_validados import TrechoValidado
from fastapi.responses import JSONResponse
import zipfile
import io
import geopandas as gpd
from datetime import datetime
import tempfile
import os
from geoalchemy2 import WKTElement

router = APIRouter()

@router.get("/validar")
def validar_geometria(db: Session = Depends(get_db)):
    try:
        zip_entry = db.query(ArquivoZip).order_by(ArquivoZip.id.desc()).first()
        if not zip_entry:
            raise HTTPException(status_code=404, detail="Nenhum arquivo encontrado para validar.")

        nome_arquivo = zip_entry.nome_arquivo
        possui_arquivos_obrigatorios = False
        geometria_valida = False
        epsg_detectado = None
        epsg_correto = False
        tipo_geometria = None
        contagem_feicoes = 0
        erros = []

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_stream = io.BytesIO(zip_entry.dados)

            with zipfile.ZipFile(zip_stream, "r") as zip_ref:
                zip_ref.extractall(tmpdir)
                file_list = zip_ref.namelist()

            required_exts = [".shp", ".shx", ".dbf", ".prj"]
            possui_arquivos_obrigatorios = all(any(f.endswith(ext) for f in file_list) for ext in required_exts)

            if not possui_arquivos_obrigatorios:
                erros.append("O arquivo .zip está incompleto (falta .shp, .shx, .dbf ou .prj).")

            shp_path = None
            for f in os.listdir(tmpdir):
                if f.endswith(".shp"):
                    shp_path = os.path.join(tmpdir, f)
                    break

            if not shp_path:
                raise HTTPException(status_code=400, detail="Arquivo .shp não encontrado no ZIP.")

            gdf = gpd.read_file(shp_path)
            contagem_feicoes = len(gdf)

        if gdf.crs:
            epsg_detectado = gdf.crs.to_epsg()
            epsg_correto = epsg_detectado == 4674
        else:
            erros.append("Não foi possível identificar o EPSG do shapefile.")

        if not epsg_correto:
            erros.append("O EPSG detectado não é 4674.")

        if "Cod" not in gdf.columns:
            erros.append("O campo 'Cod' é obrigatório e não foi encontrado.")
        elif gdf["Cod"].isnull().any() or (gdf["Cod"].astype(str).str.strip() == "").any():
            erros.append("Existem feições com o campo 'Cod' em branco ou nulo.")

        if gdf["geometry"].isnull().any():
            erros.append("Existem feições com geometria nula.")
        else:
            tipo_geometria = gdf.geometry.type.mode().iloc[0]
            if not all(gdf.geometry.type.isin(["LineString", "MultiLineString"])):
                erros.append("A geometria deve ser do tipo LINESTRING ou MULTILINESTRING.")

        geometria_valida = len(erros) == 0

        validacao = ValidacaoGeometria(
            nome_arquivo=nome_arquivo,
            possui_arquivos_obrigatorios=possui_arquivos_obrigatorios,
            geometria_valida=geometria_valida,
            epsg_detectado=epsg_detectado,
            epsg_correto=epsg_correto,
            tipo_geometria=tipo_geometria,
            contagem_feicoes=contagem_feicoes,
            data_validacao=datetime.utcnow()
        )

        db.add(validacao)
        db.commit()
        db.refresh(validacao)

        if geometria_valida:
            for _, row in gdf.iterrows():
                geometria = WKTElement(row.geometry.wkt, srid=4674)
                trecho = TrechoValidado(codigo=str(row["Cod"]), geometry=geometria)
                db.add(trecho)
            db.commit()
            return JSONResponse(content={"validado": True, "mensagem": "Geometria validada com sucesso!"})
        else:
            # Apaga trechos se a validação falhar
            db.execute("DELETE FROM trechos_validados")
            db.commit()
            return JSONResponse(content={"validado": False, "erros": erros})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar geometria: {str(e)}")
