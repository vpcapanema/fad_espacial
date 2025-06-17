from fastapi import APIRouter, HTTPException, Body, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_obra_arte_estadualizacao import ObraArteEstadualizacao
from datetime import datetime
import re
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api/cd", tags=['Cadastro de Obra de Arte'])
templates = Jinja2Templates(directory="app/templates")

def capitalizar_nome(s):
    """Capitaliza nomes próprios, mantendo preposições em minúsculo"""
    if not s: 
        return s
    preps = {"da", "de", "do", "das", "dos", "e"}
    return ' '.join([w if w in preps else w.capitalize() for w in s.lower().split()])

@router.post("/obra-arte/cadastrar", status_code=201)
def cadastrar_obra_arte(dados: dict = Body(...), db: Session = Depends(get_db)):
    """
    Cadastra uma nova obra de arte rodoviária no sistema
    Campos padronizados: id, codigo, denominacao, tipo, municipio, extensao_km, criado_em
    """
    
    # Campos obrigatórios
    campos_obrigatorios = ['codigo', 'denominacao', 'tipo', 'municipio']
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
            detail="Código deve seguir o padrão: duas ou mais letras maiúsculas, hífen, três ou mais dígitos (ex: OA-001)"
        )
    
    # Validação do tipo
    tipos_validos = ['ponte', 'viaduto', 'tunel', 'passarela', 'bueiro', 'galeria']
    if dados['tipo'].lower() not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo deve ser um dos seguintes: {', '.join(tipos_validos)}"
        )
    
    try:
        # Verificar se código já existe
        obra_existente = db.query(ObraArteEstadualizacao).filter(
            ObraArteEstadualizacao.codigo == dados['codigo']
        ).first()
        
        if obra_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Obra de arte com código '{dados['codigo']}' já está cadastrada"
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
        dados['tipo'] = dados['tipo'].lower()
        
        # Cria nova obra de arte
        nova_obra = ObraArteEstadualizacao(
            codigo=dados['codigo'],
            denominacao=dados['denominacao'],
            tipo=dados['tipo'],
            municipio=dados['municipio'],
            extensao_km=extensao_km,
            criado_em=datetime.utcnow()
        )
        
        db.add(nova_obra)
        db.commit()
        db.refresh(nova_obra)
        
        return {
            "success": True,
            "message": "Obra de arte cadastrada com sucesso",
            "id": nova_obra.id,
            "codigo": nova_obra.codigo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao cadastrar obra de arte: {str(e)}"
        )

@router.get("/obra-arte/listar")
def listar_obras_arte(db: Session = Depends(get_db)):
    """
    Lista todas as obras de arte cadastradas
    """
    try:
        obras = db.query(ObraArteEstadualizacao).order_by(ObraArteEstadualizacao.codigo).all()
        
        return {
            "success": True,
            "total": len(obras),
            "data": [
                {
                    "id": obra.id,
                    "codigo": obra.codigo,
                    "denominacao": obra.denominacao,
                    "tipo": obra.tipo,
                    "municipio": obra.municipio,
                    "extensao_km": obra.extensao_km,
                    "criado_em": obra.criado_em.isoformat() if obra.criado_em else None
                }
                for obra in obras
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar obras de arte: {str(e)}"
        )

@router.get("/obra-arte/{obra_id}")
def obter_obra_arte_por_id(obra_id: int, db: Session = Depends(get_db)):
    """
    Obtém uma obra de arte específica pelo ID
    """
    try:
        obra = db.query(ObraArteEstadualizacao).filter(ObraArteEstadualizacao.id == obra_id).first()
        
        if not obra:
            raise HTTPException(
                status_code=404,
                detail="Obra de arte não encontrada"
            )
        
        return {
            "success": True,
            "data": {
                "id": obra.id,
                "codigo": obra.codigo,
                "denominacao": obra.denominacao,
                "tipo": obra.tipo,
                "municipio": obra.municipio,
                "extensao_km": obra.extensao_km,
                "criado_em": obra.criado_em.isoformat() if obra.criado_em else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter obra de arte: {str(e)}"
        )

@router.get("/cadastrar-obra-arte")
def cadastrar_obra_arte_html(request: Request):
    return templates.TemplateResponse("cd_obra_arte.html", {"request": request})
