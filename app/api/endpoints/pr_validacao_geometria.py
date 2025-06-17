from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from pathlib import Path
import zipfile

from app.database.session import get_db
from app.models.pr_geometrias_upload import GeometriaUpload
from app.models.pr_geometrias_validadas import GeometriaValidada
from app.api.endpoints.pr_salvar_temp_validacao import salvar_resultado_temporario
from app.utils.utils_gerar_relatorio_validacao import gerar_relatorio_validacao
# ✅ Padrão de roteador aplicado
from fastapi import APIRouter

router = APIRouter(
    prefix='/shape/validacao',
    tags=['Validação de Geometria']
)

router = APIRouter()

@router.get("/validar")
def validar_geometria(db: Session = Depends(get_db)):
    try:
        geom_upload = (
            db.query(GeometriaUpload)
            .filter(GeometriaUpload.arquivo != None)
            .order_by(GeometriaUpload.criado_em.desc())
            .first()
        )

        if not geom_upload:
            return JSONResponse(status_code=404, content={"validado": False, "erro": "Nenhuma geometria para validar."})

        id_geom = geom_upload.id

        def checar(query: str) -> bool:
            resultado = db.execute(text(query)).scalar()
            return bool(resultado)

        criterios = {
            "V1": checar(f"SELECT ST_SRID(geom) = 4674 FROM geometrias_upload WHERE id = {id_geom}"),
            "V2": checar(f"SELECT GeometryType(geom) = 'LINESTRING' FROM geometrias_upload WHERE id = {id_geom}"),
            "V3": checar(f"SELECT EXISTS (SELECT 1 FROM geometrias_upload WHERE id = {id_geom} AND cod IS NOT NULL AND cod != '')"),
            "V4": checar(f"SELECT COUNT(*) > 0 FROM geometrias_upload WHERE id = {id_geom}"),
            "V5": checar(f"SELECT NOT ST_IsEmpty(geom) FROM geometrias_upload WHERE id = {id_geom}"),
            "V6": checar(f"SELECT ST_IsValid(geom) FROM geometrias_upload WHERE id = {id_geom}"),
            "V7": checar(f'''
                SELECT ST_Within(
                    geom,
                    (SELECT geom FROM "DataGEO".limite_estadual WHERE uf = 'SP' LIMIT 1)
                )
                FROM geometrias_upload WHERE id = {id_geom}
            '''),
            "V8": checar(f'''
                SELECT NOT EXISTS (
                    SELECT 1
                    FROM geometrias_upload AS a, geometrias_upload AS b
                    WHERE a.id != b.id AND ST_Overlaps(a.geom, b.geom)
                )
            '''),
            "V9": checar(f"SELECT ST_Length(geom::geography) > 10 FROM geometrias_upload WHERE id = {id_geom}")
        }

        aprovado = all(criterios.values())

        id_validacao = salvar_resultado_temporario(
            db=db,
            id_geom_upload=id_geom,
            criterios=criterios,
            aprovado=aprovado
        )

        nome_pdf = f"validacao_{id_validacao}.pdf"
        gerar_relatorio_validacao(
            usuario=geom_upload,
            resultados_dict=criterios,
            erros=[] if aprovado else ["Critérios não atendidos"],
            aprovado=aprovado,
            nome_pdf=nome_pdf
        )

        if aprovado:
            geom_validada = GeometriaValidada(
                projeto_id=geom_upload.projeto_id,
                usuario_id=geom_upload.usuario_id,
                cod=None,
                arquivo=geom_upload.arquivo,
                geom=geom_upload.geom,
                validado_em=datetime.utcnow()
            )
            db.add(geom_validada)
            db.commit()

        return JSONResponse(content={"validado": aprovado})

    except Exception as e:
        return JSONResponse(status_code=500, content={"validado": False, "erro": str(e)})
@router.post("/validar/{id_upload}")
def validar_geometria(id_upload: int, db: Session = Depends(get_db)):
    try:
        # Buscar upload
        upload = db.query(GeometriaUpload).filter(GeometriaUpload.upload_id == id_upload).first()
        if not upload:
            return JSONResponse(status_code=404, content={"validado": False, "erro": "Upload não encontrado."})

        # Caminho do arquivo zip
        nome_base = upload.arquivo.replace('.zip', '')
        temp_dir = Path("temp") / nome_base
        zip_path = temp_dir / upload.arquivo
        if not zip_path.exists():
            return JSONResponse(status_code=404, content={"validado": False, "erro": "Arquivo ZIP não encontrado."})

        # Checar arquivos obrigatórios
        obrigatorios = {'.shp': False, '.shx': False, '.dbf': False, '.prj': False}
        with zipfile.ZipFile(zip_path, 'r') as z:
            for f in z.namelist():
                for ext in obrigatorios:
                    if f.lower().endswith(ext):
                        obrigatorios[ext] = True
        erros = []
        if not (obrigatorios['.shp'] and obrigatorios['.shx'] and obrigatorios['.dbf']):
            erros.append("Faltam arquivos obrigatórios (.shp, .shx, .dbf). Upload reprovado.")
        if not obrigatorios['.prj']:
            # Aqui você pode chamar função para reprojetar para EPSG 5880 (mock)
            pass # Implementar reprojeção se necessário
        # Checar campo cod
        if not upload.n_cod_trecho_preenchido or upload.n_cod_trecho_preenchido == 0:
            erros.append("Campo 'cod' não preenchido.")
        # Checar topologia, comprimento, sobreposição, dentro de SP, etc (mock)
        # ...
        # Se houver erros, gerar relatório e reprovar
        if erros:
            nome_pdf = f"validacao_{upload.id}_erro.pdf"
            gerar_relatorio_validacao(
                usuario=upload,
                resultados_dict={},
                erros=erros,
                aprovado=False,
                nome_pdf=nome_pdf
            )
            return JSONResponse(status_code=400, content={
                "validado": False,
                "mensagem": "Geometria reprovada.",
                "relatorio": f"/static/relatorios/{nome_pdf}",
                "erros": erros
            })
        # Se aprovado, gerar relatório de sucesso
        nome_pdf = f"validacao_{upload.id}_ok.pdf"
        gerar_relatorio_validacao(
            usuario=upload,
            resultados_dict={"arquivos_obrigatorios": True, "cod_preenchido": True},
            erros=[],
            aprovado=True,
            nome_pdf=nome_pdf
        )
        return JSONResponse(content={
            "validado": True,
            "mensagem": "Geometria validada com sucesso.",
            "relatorio": f"/static/relatorios/{nome_pdf}"
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"validado": False, "erro": str(e)})
