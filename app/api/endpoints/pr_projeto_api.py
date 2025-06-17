from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.validacao_geometria import ValidadorZipShapefile, ValidadorGeometria
import json

router = APIRouter(prefix="/api/projeto", tags=["Projeto API"])

@router.post("/validar-geometria")
async def validar_geometria(arquivo_zip: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    ETAPA 2: Validação do ZIP e Geometria
    
    Fluxo:
    1. Valida ZIP → Se erro: PDF de erro + interrompe
    2. Extrai arquivos → Salva na tabela temporária  
    3. Valida geometria → Se erro: PDF de erro + interrompe
    4. Salva geometria validada → PDF de sucesso
    """
    try:
        # Ler conteúdo do arquivo
        conteudo_zip = await arquivo_zip.read()
        
        # FASE 1: Validação do ZIP
        validador_zip = ValidadorZipShapefile(db)
        resultado_zip = validador_zip.validar_zip(conteudo_zip, arquivo_zip.filename)
        
        if resultado_zip['status'] == 'erro':
            return JSONResponse(resultado_zip)
        
        # FASE 2: Validação da Geometria
        validador_geometria = ValidadorGeometria(db)
        resultado_geometria = validador_geometria.validar_geometria(resultado_zip['projeto_temp_id'])
        
        if resultado_geometria['status'] == 'erro':
            return JSONResponse(resultado_geometria)
        
        # Sucesso completo
        return JSONResponse({
            "status": "sucesso",
            "projeto_temp_id": resultado_geometria['projeto_temp_id'],
            "mensagem": "ZIP e geometria validados com sucesso!",
            "pdf_relatorio": resultado_geometria['pdf_sucesso_path'],
            "geometria_dados": resultado_geometria['geometria_dados'],
            "proximo_passo": "visualizar_mapa"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "erro",
            "mensagem": f"Erro inesperado: {str(e)}"
        })

@router.post("/gerar-croqui")
async def gerar_croqui(dados: dict, db: Session = Depends(get_db)):
    """
    ETAPA 4: Gera croqui baseado no estado atual do mapa Leaflet
    """
    try:
        from app.services.projeto_finalizacao import GeradorCroqui
        
        gerador = GeradorCroqui(db)
        resultado = gerador.gerar_croqui(
            dados['projeto_temp_id'],
            dados['dados_mapa']
        )
        
        return JSONResponse(resultado)
        
    except Exception as e:
        return JSONResponse({
            "status": "erro",
            "mensagem": f"Erro ao gerar croqui: {str(e)}"
        })

@router.post("/finalizar")
async def finalizar_projeto(dados: dict, db: Session = Depends(get_db)):
    """
    ETAPA 5: Finaliza projeto e gera relatórios completos
    """
    try:
        from app.services.projeto_finalizacao import FinalizadorProjeto
        
        finalizador = FinalizadorProjeto(db)
        resultado = finalizador.finalizar_projeto(dados)
        
        return JSONResponse(resultado)
        
    except Exception as e:
        return JSONResponse({
            "status": "erro",
            "mensagem": f"Erro ao finalizar projeto: {str(e)}"
        })
        
@router.get("/geometria-mapa/{projeto_temp_id}")
async def obter_geometria_para_mapa(projeto_temp_id: str, db: Session = Depends(get_db)):
    """
    ETAPA 3: Carrega geometria validada e malha DER para o mapa
    """
    try:
        from app.models.pr_projeto_geometria import GeometriaValidada, MalhaDer2025
        
        # Buscar geometria validada
        geometria = db.query(GeometriaValidada).filter(
            GeometriaValidada.projeto_temp_id == projeto_temp_id
        ).first()
        
        if not geometria:
            return JSONResponse({
                "status": "erro",
                "mensagem": "Geometria validada não encontrada"
            })
        
        # Buscar malha DER (simplificada para o mapa)
        malha_der = db.query(MalhaDer2025).filter(
            MalhaDer2025.ativo == True
        ).all()
        
        # Preparar dados para o mapa
        geometria_dados = {
            "wkt": geometria.geom_wkt,
            "centroide": {
                "lat": geometria.centroide_lat,
                "lon": geometria.centroide_lon
            },
            "bbox": {
                "min_x": geometria.bbox_min_x,
                "min_y": geometria.bbox_min_y,
                "max_x": geometria.bbox_max_x,
                "max_y": geometria.bbox_max_y
            }
        }
        
        malha_dados = [
            {
                "codigo": rodovia.codigo_rodovia,
                "nome": rodovia.nome_rodovia,
                "tipo": rodovia.tipo_rodovia,
                "wkt": rodovia.geom_wkt
            }
            for rodovia in malha_der[:50]  # Limitar para performance
        ]
        
        return JSONResponse({
            "status": "sucesso",
            "geometria_projeto": geometria_dados,
            "malha_der": malha_dados,
            "zoom_sugerido": 12
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "erro",
            "mensagem": f"Erro ao carregar dados para mapa: {str(e)}"
        })
