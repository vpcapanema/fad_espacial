from fastapi import APIRouter, HTTPException, Body, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_rodovia_estadualizacao import RodoviaEstadualizacao
from datetime import datetime
import re
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api/cd", tags=['Cadastro de Rodovia'])

templates = Jinja2Templates(directory="app/templates")

def capitalizar_nome(s):
    """Capitaliza nomes próprios, mantendo preposições em minúsculo"""
    if not s: 
        return s
    preps = {"da", "de", "do", "das", "dos", "e"}
    return ' '.join([w if w in preps else w.capitalize() for w in s.lower().split()])

@router.post("/rodovia/cadastrar", status_code=201)
def cadastrar_rodovia(dados: dict = Body(...), db: Session = Depends(get_db)):
    """
    Cadastra uma nova rodovia no sistema
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
            detail="Código deve seguir o padrão: duas ou mais letras maiúsculas, hífen, três ou mais dígitos (ex: RO-001)"
        )
    
    try:
        # Verificar se código já existe
        rodovia_existente = db.query(RodoviaEstadualizacao).filter(
            RodoviaEstadualizacao.codigo == dados['codigo']
        ).first()
        
        if rodovia_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Rodovia com código '{dados['codigo']}' já está cadastrada"
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
        
        # Cria nova rodovia
        nova_rodovia = RodoviaEstadualizacao(
            codigo=dados['codigo'],
            denominacao=dados['denominacao'],
            municipio=dados.get('municipio'),
            extensao_km=extensao_km,
            tipo=dados.get('tipo'),
            criado_em=datetime.utcnow()
        )
        
        db.add(nova_rodovia)
        db.commit()
        db.refresh(nova_rodovia)
        
        return {
            "success": True,
            "message": "Rodovia cadastrada com sucesso",
            "id": nova_rodovia.id,
            "codigo": nova_rodovia.codigo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao cadastrar rodovia: {str(e)}"
        )

@router.get("/rodovia/listar")
def listar_rodovias(db: Session = Depends(get_db)):
    """
    Lista todas as rodovias cadastradas
    """
    try:
        rodovias = db.query(RodoviaEstadualizacao).order_by(RodoviaEstadualizacao.codigo).all()
        
        return {
            "success": True,
            "total": len(rodovias),
            "data": [
                {
                    "id": rodovia.id,
                    "codigo": rodovia.codigo,
                    "denominacao": rodovia.denominacao,
                    "tipo": rodovia.tipo,
                    "municipio": rodovia.municipio,
                    "extensao_km": rodovia.extensao_km,
                    "criado_em": rodovia.criado_em.isoformat() if rodovia.criado_em else None
                }
                for rodovia in rodovias
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar rodovias: {str(e)}"
        )

@router.get("/rodovia/{rodovia_id}")
def obter_rodovia_por_id(rodovia_id: int, db: Session = Depends(get_db)):
    """
    Obtém uma rodovia específica pelo ID
    """
    try:
        rodovia = db.query(RodoviaEstadualizacao).filter(RodoviaEstadualizacao.id == rodovia_id).first()
        
        if not rodovia:
            raise HTTPException(
                status_code=404,
                detail="Rodovia não encontrada"
            )
        
        return {
            "success": True,
            "data": {
                "id": rodovia.id,
                "codigo": rodovia.codigo,
                "denominacao": rodovia.denominacao,
                "tipo": rodovia.tipo,
                "municipio": rodovia.municipio,
                "extensao_km": rodovia.extensao_km,
                "criado_em": rodovia.criado_em.isoformat() if rodovia.criado_em else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter rodovia: {str(e)}"
        )

@router.get("/cadastrar-rodovia")
def cadastrar_rodovia_html(request: Request):
    return templates.TemplateResponse("cd_rodovia.html", {"request": request})
