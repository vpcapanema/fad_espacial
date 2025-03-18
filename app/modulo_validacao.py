import zipfile
import geopandas as gpd
import os
import io
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.database import get_db, DATABASE_URL
from app.models import ValidacaoGeometria

router = APIRouter()

# EPSG esperado para cruzamento
EPSG_PADRAO = 4326  

@router.post("/validar_shapefile/")
async def validar_shapefile(arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    # Armazenar o conteúdo do arquivo ZIP na memória
    conteudo_zip = await arquivo.read()
    zip_stream = io.BytesIO(conteudo_zip)

    # Criar um diretório temporário na memória para extrair os arquivos ZIP
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_stream, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Verificar se o ZIP contém os arquivos obrigatórios
        obrigatorios = {".shp", ".shx", ".prj", ".dbf"}
        encontrados = {os.path.splitext(f)[1] for f in os.listdir(temp_dir)}

        possui_arquivos_obrigatorios = obrigatorios.issubset(encontrados)
        if not possui_arquivos_obrigatorios:
            raise HTTPException(status_code=400, detail="ZIP não contém todos os arquivos essenciais (.shp, .shx, .prj, .dbf).")

        # Identificar o arquivo .shp
        shp_file = next((os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".shp")), None)

        if not shp_file:
            raise HTTPException(status_code=400, detail="Arquivo .shp não encontrado no ZIP.")

        # Ler o shapefile com GeoPandas diretamente da memória
        try:
            gdf = gpd.read_file(shp_file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao ler o shapefile: {str(e)}")

        # Verificar se a geometria não é nula
        geometria_valida = not gdf.empty and not gdf.geometry.isnull().all()

        # Verificar o EPSG do shapefile
        epsg_correto = gdf.crs is not None and gdf.crs.to_epsg() == EPSG_PADRAO
        epsg_detectado = gdf.crs.to_epsg() if gdf.crs else None

        # Identificar tipo geométrico e contagem de feições
        tipo_geometria = ", ".join(gdf.geom_type.unique().tolist())
        contagem_feicoes = len(gdf)

        # Se o arquivo for válido, salvar no banco PostGIS
        if geometria_valida and epsg_correto:
            engine = create_engine(DATABASE_URL)
            gdf.to_postgis("dados_geoespaciais", engine, if_exists="append", index=False)
        else:
            raise HTTPException(status_code=400, detail="Arquivo inválido, não será salvo no banco.")

        # Salvar no banco de validação
        resultado = ValidacaoGeometria(
            nome_arquivo=os.path.basename(shp_file),
            possui_arquivos_obrigatorios=possui_arquivos_obrigatorios,
            geometria_valida=geometria_valida,
            epsg_correto=epsg_correto,
            epsg_detectado=epsg_detectado,
            tipo_geometria=tipo_geometria,
            contagem_feicoes=contagem_feicoes
        )
        
        db.add(resultado)
        db.commit()

        return {
            "mensagem": "Validação concluída",
            "arquivo": os.path.basename(shp_file),
            "possui_arquivos_obrigatorios": possui_arquivos_obrigatorios,
            "geometria_valida": geometria_valida,
            "epsg_correto": epsg_correto,
            "epsg_detectado": epsg_detectado,
            "tipo_geometria": tipo_geometria,
            "contagem_feicoes": contagem_feicoes
        }
