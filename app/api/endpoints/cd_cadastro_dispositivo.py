from fastapi import APIRouter, HTTPException, Body, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_dispositivo_estadualizacao import DispositivoEstadualizacao
from datetime import datetime
import re
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api/cd", tags=['Cadastro de Dispositivo'])
templates = Jinja2Templates(directory="app/templates")

def capitalizar_nome(s):
    """Capitaliza nomes próprios, mantendo preposições em minúsculo"""
    if not s: 
        return s
    preps = {"da", "de", "do", "das", "dos", "e"}
    return ' '.join([w if w in preps else w.capitalize() for w in s.lower().split()])

@router.post("/dispositivo/cadastrar", status_code=201)
def cadastrar_dispositivo(dados: dict = Body(...), db: Session = Depends(get_db)):
    """
    Cadastra um novo dispositivo rodoviário no sistema
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
            detail="Código deve seguir o padrão: duas ou mais letras maiúsculas, hífen, três ou mais dígitos (ex: DI-001)"
        )
    
    # Validação do tipo
    tipos_validos = ['viaduto', 'ponte', 'tunel', 'passarela', 'rotatoria', 'acesso', 'retorno']
    if dados['tipo'].lower() not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo deve ser um dos seguintes: {', '.join(tipos_validos)}"
        )
    
    try:
        # Verificar se código já existe
        dispositivo_existente = db.query(DispositivoEstadualizacao).filter(
            DispositivoEstadualizacao.codigo == dados['codigo']
        ).first()
        
        if dispositivo_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Dispositivo com código '{dados['codigo']}' já está cadastrado"
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
        
        # Cria novo dispositivo
        novo_dispositivo = DispositivoEstadualizacao(
            codigo=dados['codigo'],
            denominacao=dados['denominacao'],
            tipo=dados['tipo'],
            municipio=dados['municipio'],
            extensao_km=extensao_km,
            criado_em=datetime.utcnow()
        )
        
        db.add(novo_dispositivo)
        db.commit()
        db.refresh(novo_dispositivo)
        
        return {
            "success": True,
            "message": "Dispositivo cadastrado com sucesso",
            "id": novo_dispositivo.id,
            "codigo": novo_dispositivo.codigo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao cadastrar dispositivo: {str(e)}"
        )

@router.get("/dispositivo/listar")
def listar_dispositivos(db: Session = Depends(get_db)):
    """
    Lista todos os dispositivos cadastrados
    """
    try:
        dispositivos = db.query(DispositivoEstadualizacao).order_by(DispositivoEstadualizacao.codigo).all()
        
        return {
            "success": True,
            "total": len(dispositivos),
            "data": [
                {
                    "id": dispositivo.id,
                    "codigo": dispositivo.codigo,
                    "denominacao": dispositivo.denominacao,
                    "tipo": dispositivo.tipo,
                    "municipio": dispositivo.municipio,
                    "extensao_km": dispositivo.extensao_km,
                    "criado_em": dispositivo.criado_em.isoformat() if dispositivo.criado_em else None
                }
                for dispositivo in dispositivos
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar dispositivos: {str(e)}"
        )

@router.get("/dispositivo/{dispositivo_id}")
def obter_dispositivo_por_id(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Obtém um dispositivo específico pelo ID
    """
    try:
        dispositivo = db.query(DispositivoEstadualizacao).filter(DispositivoEstadualizacao.id == dispositivo_id).first()
        
        if not dispositivo:
            raise HTTPException(
                status_code=404,
                detail="Dispositivo não encontrado"
            )
        
        return {
            "success": True,
            "data": {
                "id": dispositivo.id,
                "codigo": dispositivo.codigo,
                "denominacao": dispositivo.denominacao,
                "tipo": dispositivo.tipo,
                "municipio": dispositivo.municipio,
                "extensao_km": dispositivo.extensao_km,
                "criado_em": dispositivo.criado_em.isoformat() if dispositivo.criado_em else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter dispositivo: {str(e)}"
        )

@router.get("/cadastrar-dispositivo")
def cadastrar_dispositivo_html(request: Request):
    return templates.TemplateResponse("cd_dispositivo.html", {"request": request})
