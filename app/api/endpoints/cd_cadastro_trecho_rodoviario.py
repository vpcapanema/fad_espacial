from fastapi import APIRouter, HTTPException, Body, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from datetime import datetime
import re
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api/cd", tags=['Cadastro de Trecho Rodoviário'])
templates = Jinja2Templates(directory="app/templates")

def capitalizar_nome(s):
    """Capitaliza nomes próprios, mantendo preposições em minúsculo"""
    if not s: 
        return s
    preps = {"da", "de", "do", "das", "dos", "e"}
    return ' '.join([w if w in preps else w.capitalize() for w in s.lower().split()])

@router.post("/trecho-rodoviario/cadastrar", status_code=201)
def cadastrar_trecho_rodoviario(dados: dict = Body(...), db: Session = Depends(get_db)):
    """
    Cadastra um novo trecho rodoviário no sistema
    Campos padronizados: id, codigo, denominacao, tipo, municipio, extensao_km, criado_em
    """
    
    # Campos obrigatórios
    campos_obrigatorios = ['codigo', 'denominacao', 'municipio']
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            raise HTTPException(
                status_code=400, 
                detail=f"Campo obrigatório ausente: {campo}"
            )
    
    # Validação do código do elemento rodoviário
    regex_codigo = r'^[A-Z]{2,}-\d{3,}$'
    if not re.match(regex_codigo, dados['codigo']):
        raise HTTPException(
            status_code=400,
            detail="Código deve seguir o padrão: duas ou mais letras maiúsculas, hífen, três ou mais dígitos (ex: TR-001)"
        )
    
    try:
        # Verificar se código já existe
        trecho_existente = db.query(TrechoEstadualizacao).filter(
            TrechoEstadualizacao.codigo == dados['codigo']
        ).first()
        
        if trecho_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Trecho rodoviário com código '{dados['codigo']}' já está cadastrado"
            )
        
        # Validação da extensão
        extensao_km = None
        if dados.get('extensao_km'):
            try:
                extensao_km = float(dados['extensao_km'])
                if extensao_km <= 0:
                    raise ValueError("Extensão deve ser maior que zero")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Extensão deve ser um número válido maior que zero"
                )
        
        # Padronização de campos antes de gravar
        dados['denominacao'] = capitalizar_nome(dados.get('denominacao', ''))
        dados['municipio'] = capitalizar_nome(dados.get('municipio', ''))
        
        # Cria novo trecho rodoviário
        novo_trecho = TrechoEstadualizacao(
            codigo=dados['codigo'],
            denominacao=dados['denominacao'],
            municipio=dados['municipio'],
            extensao_km=extensao_km,
            tipo=dados.get('tipo'),
            criado_em=datetime.utcnow()
        )
        
        db.add(novo_trecho)
        db.commit()
        db.refresh(novo_trecho)
        
        return {
            "success": True,
            "message": "Trecho rodoviário cadastrado com sucesso",
            "id": novo_trecho.id,
            "codigo": novo_trecho.codigo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao cadastrar trecho rodoviário: {str(e)}"
        )

@router.get("/trecho-rodoviario/listar")
def listar_trechos_rodoviarios(db: Session = Depends(get_db)):
    """
    Lista todos os trechos rodoviários cadastrados
    """
    try:
        trechos = db.query(TrechoEstadualizacao).order_by(TrechoEstadualizacao.codigo).all()
        
        return {
            "success": True,
            "total": len(trechos),
            "data": [
                {
                    "id": trecho.id,
                    "codigo": trecho.codigo,
                    "denominacao": trecho.denominacao,
                    "tipo": trecho.tipo,
                    "municipio": trecho.municipio,
                    "extensao_km": trecho.extensao_km,
                    "criado_em": trecho.criado_em.isoformat() if trecho.criado_em else None
                }
                for trecho in trechos
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar trechos rodoviários: {str(e)}"
        )

@router.get("/trecho-rodoviario/{trecho_id}")
def obter_trecho_por_id(trecho_id: int, db: Session = Depends(get_db)):
    """
    Obtém um trecho rodoviário específico pelo ID
    """
    try:
        trecho = db.query(TrechoEstadualizacao).filter(TrechoEstadualizacao.id == trecho_id).first()
        
        if not trecho:
            raise HTTPException(
                status_code=404,
                detail="Trecho rodoviário não encontrado"
            )
        
        return {
            "success": True,
            "data": {
                "id": trecho.id,
                "codigo": trecho.codigo,
                "denominacao": trecho.denominacao,
                "tipo": trecho.tipo,
                "municipio": trecho.municipio,
                "extensao_km": trecho.extensao_km,
                "criado_em": trecho.criado_em.isoformat() if trecho.criado_em else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter trecho rodoviário: {str(e)}"
        )

@router.get("/cadastrar-trecho-rodoviario")
def cadastrar_trecho_rodoviario_html(request: Request):
    return templates.TemplateResponse("cd_trecho.html", {"request": request})
