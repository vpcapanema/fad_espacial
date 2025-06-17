from fastapi import APIRouter, Request, Depends, HTTPException, Body, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.session import get_db
from app.models.cd_pessoa_fisica import PessoaFisica, registrar_auditoria_pessoa_fisica
from app.models.cd_pessoa_juridica import PessoaJuridica
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from datetime import datetime
import re

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Página de cadastro de PF (interface HTML)
@router.get("/cadastrar-pessoa-fisica")
def interessado_pf(request: Request, db: Session = Depends(get_db)):
    print("[LOG PF] Acessando página de cadastro de pessoa física")
    try:
        # Pessoa física é independente - não precisa carregar PJs nem trechos
        return templates.TemplateResponse("cd_interessado_pf.html", {
            "request": request
        })
    except Exception as e:
        print(f"[LOG PF] Erro ao carregar página: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

# 🔄 Endpoint JSON para atualização da lista de PFs
@router.get("/cadastro/pfs/json")
def listar_pfs_json(db: Session = Depends(get_db)):
    print("[LOG PF] Carregando lista de pessoas físicas para JSON")
    try:
        pfs = db.query(PessoaFisica).all()
        print(f"[LOG PF] Encontradas {len(pfs)} pessoas físicas")
        return [
            {
                "id": pf.id,
                "nome": pf.nome,
                "cpf": pf.cpf,
                "email": pf.email,
                "telefone": pf.telefone
            }
            for pf in pfs
        ]
    except Exception as e:
        print(f"[LOG PF] Erro ao carregar lista de pessoas físicas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao carregar lista de pessoas físicas")

# 🔄 Endpoint JSON para atualização da lista de PJs
@router.get("/cadastro/pjs/json")
def listar_pjs_json(db: Session = Depends(get_db)):
    pjs = db.query(PessoaJuridica).all()
    return [
        {
            "id": pj.id,
            "razao_social": pj.razao_social,
            "cnpj": pj.cnpj
        }
        for pj in pjs
    ]

# 🔄 Endpoint JSON para atualização da lista de Trechos
@router.get("/cadastro/trechos/json")
def listar_trechos_json(db: Session = Depends(get_db)):
    trechos = db.query(TrechoEstadualizacao).all()
    return [
        {
            "id": t.id,
            "codigo": t.codigo,
            "denominacao": t.denominacao,
            "municipio": t.municipio
        }
        for t in trechos
    ]

@router.put("/cadastro/pessoa-fisica/{pf_id}")
def editar_pessoa_fisica(pf_id: int, dados: dict = Body(...), db: Session = Depends(get_db), usuario: str = "sistema"):
    pf = db.query(PessoaFisica).filter(PessoaFisica.id == pf_id).first()
    if not pf:
        raise HTTPException(status_code=404, detail="Pessoa Física não encontrada")
    # Copia o estado antigo para auditoria
    import copy
    pf_antiga = copy.deepcopy(pf)
    # Atualiza campos
    campos_editaveis = [
        'nome', 'cpf', 'email', 'telefone', 'rua', 'numero', 'bairro',
        'municipio', 'uf', 'cep', 'complemento'
    ]
    for campo in campos_editaveis:
        if campo in dados:
            setattr(pf, campo, dados[campo])
    pf.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(pf)
    # Auditoria
    registrar_auditoria_pessoa_fisica(db, pf_antiga, pf, usuario)
    return {"msg": "Pessoa Física atualizada com sucesso", "id": pf.id}

def validar_cpf(cpf: str) -> bool:
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

@router.get("/validar-cpf/{cpf}")
def validar_cpf_endpoint(cpf: str, db: Session = Depends(get_db)):
    if not validar_cpf(cpf):
        return {"valido": False, "motivo": "CPF inválido"}
    existe = db.query(PessoaFisica).filter(PessoaFisica.cpf == cpf).first()
    if existe:
        return {"valido": False, "motivo": "CPF já cadastrado"}
    return {"valido": True}

@router.post("/cadastrar-pessoa-fisica", status_code=status.HTTP_201_CREATED)
def cadastrar_pessoa_fisica(dados: dict = Body(...), db: Session = Depends(get_db)):
    print(f"[LOG PF] Recebida requisição para cadastrar pessoa física: {dados}")
    campos_obrigatorios = [
        'nome', 'cpf', 'email', 'telefone', 'logradouro', 'numero', 'bairro', 'cep', 'municipio', 'uf'
    ]
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            print(f"[LOG PF] Campo obrigatório ausente: {campo}")
            raise HTTPException(status_code=400, detail=f"Campo obrigatório ausente: {campo}")
    # Normaliza CPF
    cpf_limpo = re.sub(r"\D", "", dados['cpf'])
    if db.query(PessoaFisica).filter(PessoaFisica.cpf == cpf_limpo).first():
        print("[LOG PF] CPF já cadastrado")
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    pf = PessoaFisica(
        nome=dados['nome'],
        cpf=cpf_limpo,
        email=dados['email'],
        telefone=dados['telefone'],
        logradouro=dados['logradouro'],
        numero=dados['numero'],
        complemento=dados.get('complemento'),
        bairro=dados['bairro'],
        cep=dados['cep'],
        municipio=dados['municipio'],
        uf=dados['uf'],
        criado_em=datetime.utcnow()
    )
    db.add(pf)
    try:
        db.commit()
        db.refresh(pf)
    except IntegrityError as e:
        print(f"[LOG PF] Erro de integridade ao cadastrar PF: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade ao cadastrar PF")
    print(f"[LOG PF] Pessoa Física cadastrada com sucesso: {pf.id}")
    return {"msg": "Pessoa Física cadastrada com sucesso", "id": pf.id}
