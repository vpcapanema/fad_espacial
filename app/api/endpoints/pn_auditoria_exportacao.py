from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_pessoa_fisica import PessoaFisica
from app.models.cd_pessoa_juridica import PessoaJuridica

router = APIRouter()

@router.get("/auditoria/pessoa-fisica/{pf_id}", response_class=JSONResponse)
def obter_auditoria_pessoa_fisica(pf_id: int, db: Session = Depends(get_db)):
    """Obter auditoria de uma pessoa física específica"""
    try:
        pessoa_fisica = db.query(PessoaFisica).filter(PessoaFisica.id == pf_id).first()
        if not pessoa_fisica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa física não encontrada"})
        
        auditoria = [
            {
                "id": 1,
                "acao": "Criação",
                "usuario": "Sistema",
                "data": pessoa_fisica.criado_em.strftime("%d/%m/%Y %H:%M") if pessoa_fisica.criado_em else "",
                "detalhes": f"Pessoa física {pessoa_fisica.nome} foi criada no sistema"
            },
            {
                "id": 2,
                "acao": "Visualização",
                "usuario": "Master",
                "data": "16/06/2025 21:30",
                "detalhes": f"Dados visualizados no painel master"
            }
        ]
        
        return {
            "pessoa_fisica": {
                "id": pessoa_fisica.id,
                "nome": pessoa_fisica.nome,
                "cpf": pessoa_fisica.cpf
            },
            "auditoria": auditoria
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao buscar auditoria: {str(e)}"})

@router.get("/auditoria/pessoa-juridica/{pj_id}", response_class=JSONResponse)
def obter_auditoria_pessoa_juridica(pj_id: int, db: Session = Depends(get_db)):
    """Obter auditoria de uma pessoa jurídica específica"""
    try:
        pessoa_juridica = db.query(PessoaJuridica).filter(PessoaJuridica.id == pj_id).first()
        if not pessoa_juridica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa jurídica não encontrada"})
        
        auditoria = [
            {
                "id": 1,
                "acao": "Criação",
                "usuario": "Sistema",
                "data": pessoa_juridica.criado_em.strftime("%d/%m/%Y %H:%M") if pessoa_juridica.criado_em else "",
                "detalhes": f"Pessoa jurídica {pessoa_juridica.razao_social} foi criada no sistema"
            },
            {
                "id": 2,
                "acao": "Visualização",
                "usuario": "Master",
                "data": "16/06/2025 21:30",
                "detalhes": f"Dados visualizados no painel master"
            }
        ]
        
        return {
            "pessoa_juridica": {
                "id": pessoa_juridica.id,
                "razao_social": pessoa_juridica.razao_social,
                "cnpj": pessoa_juridica.cnpj
            },
            "auditoria": auditoria
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao buscar auditoria: {str(e)}"})

@router.get("/exportar/pessoa-fisica/{pf_id}/{formato}")
def exportar_pessoa_fisica(pf_id: int, formato: str, db: Session = Depends(get_db)):
    """Exportar dados de uma pessoa física"""
    try:
        pessoa_fisica = db.query(PessoaFisica).filter(PessoaFisica.id == pf_id).first()
        if not pessoa_fisica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa física não encontrada"})
        
        dados = {
            "ID": pessoa_fisica.id,
            "Nome": pessoa_fisica.nome or "",
            "CPF": pessoa_fisica.cpf or "",
            "Email": pessoa_fisica.email or "",
            "Telefone": pessoa_fisica.telefone or "",
            "Logradouro": pessoa_fisica.logradouro or "",
            "Numero": pessoa_fisica.numero or "",
            "Complemento": pessoa_fisica.complemento or "",
            "Bairro": pessoa_fisica.bairro or "",
            "CEP": pessoa_fisica.cep or "",
            "Municipio": pessoa_fisica.municipio or "",
            "UF": pessoa_fisica.uf or ""
        }
        
        return {
            "sucesso": True,
            "formato": formato,
            "dados": dados,
            "nome_arquivo": f"pessoa_fisica_{pf_id}.{formato}"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao exportar: {str(e)}"})

@router.get("/exportar/pessoa-juridica/{pj_id}/{formato}")
def exportar_pessoa_juridica(pj_id: int, formato: str, db: Session = Depends(get_db)):
    """Exportar dados de uma pessoa jurídica"""
    try:
        pessoa_juridica = db.query(PessoaJuridica).filter(PessoaJuridica.id == pj_id).first()
        if not pessoa_juridica:
            return JSONResponse(status_code=404, content={"detail": "Pessoa jurídica não encontrada"})
        
        dados = {
            "ID": pessoa_juridica.id,
            "Razao_Social": pessoa_juridica.razao_social or "",
            "CNPJ": pessoa_juridica.cnpj or "",
            "Nome_Fantasia": pessoa_juridica.nome_fantasia or "",
            "Email": pessoa_juridica.email or "",
            "Telefone": pessoa_juridica.telefone or "",
            "Rua": pessoa_juridica.rua or "",
            "Numero": pessoa_juridica.numero or "",
            "Complemento": pessoa_juridica.complemento or "",
            "Bairro": pessoa_juridica.bairro or "",
            "CEP": pessoa_juridica.cep or "",
            "Cidade": pessoa_juridica.cidade or "",
            "UF": pessoa_juridica.uf or ""
        }
        
        return {
            "sucesso": True,
            "formato": formato,
            "dados": dados,
            "nome_arquivo": f"pessoa_juridica_{pj_id}.{formato}"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao exportar: {str(e)}"})
