from fastapi import APIRouter, Request, Depends, HTTPException, Body
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_pessoa_fisica import PessoaFisica
from app.models.cd_pessoa_juridica import PessoaJuridica
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from app.models.cd_pessoa_juridica import registrar_auditoria_pessoa_juridica
from datetime import datetime
import copy
import re

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Página de cadastro de PJ (interface HTML)
@router.get("/cadastrar-pessoa-juridica")
def interessado_pj(request: Request, db: Session = Depends(get_db)):
    pfs = db.query(PessoaFisica).all()
    trechos = db.query(TrechoEstadualizacao).all()
    return templates.TemplateResponse("cd_interessado_pj.html", {
        "request": request,
        "pfs": pfs,
        "trechos": trechos
    })

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

# 🔄 Endpoint JSON para atualização da lista de PFs
@router.get("/cadastro/pfs/json")
def listar_pfs_json(db: Session = Depends(get_db)):
    pfs = db.query(PessoaFisica).all()
    return [
        {
            "id": pf.id,
            "nome": pf.nome,
            "cpf": pf.cpf
        }
        for pf in pfs
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

@router.put("/cadastro/pessoa-juridica/{pj_id}")
def editar_pessoa_juridica(pj_id: int, dados: dict = Body(...), db: Session = Depends(get_db), usuario: str = "sistema"):
    pj = db.query(PessoaJuridica).filter(PessoaJuridica.id == pj_id).first()
    if not pj:
        raise HTTPException(status_code=404, detail="Pessoa Jurídica não encontrada")
    # Copia o estado antigo para auditoria
    pj_antiga = copy.deepcopy(pj)
    # Atualiza campos
    campos_editaveis = [
        'razao_social', 'cnpj', 'nome_fantasia', 'email', 'telefone', 'celular',
        'rua', 'numero', 'bairro', 'cep', 'cidade', 'uf', 'complemento'
    ]
    for campo in campos_editaveis:
        if campo in dados:
            setattr(pj, campo, dados[campo])
    pj.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(pj)
    # Auditoria
    registrar_auditoria_pessoa_juridica(db, pj_antiga, pj, usuario)
    return {"msg": "Pessoa Jurídica atualizada com sucesso", "id": pj.id}

@router.post("/cadastro/pessoa-juridica", status_code=201)
def cadastrar_pessoa_juridica(dados: dict = Body(...), db: Session = Depends(get_db)):
    print(f"[LOG PJ] Recebida requisição para cadastrar pessoa jurídica: {dados}")
    campos_obrigatorios = [
        'razao_social', 'cnpj', 'email', 'telefone', 'rua', 'numero', 'bairro', 'cep', 'cidade', 'uf'
    ]
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            print(f"[LOG PJ] Campo obrigatório ausente: {campo}")
            raise HTTPException(status_code=400, detail=f"Campo obrigatório ausente: {campo}")
    cnpj_limpo = re.sub(r"\D", "", dados['cnpj'])
    if db.query(PessoaJuridica).filter(PessoaJuridica.cnpj == cnpj_limpo).first():
        print("[LOG PJ] CNPJ já cadastrado")
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    pj = PessoaJuridica(
        razao_social=dados['razao_social'],
        cnpj=cnpj_limpo,
        nome_fantasia=dados.get('nome_fantasia'),
        email=dados['email'],
        telefone=dados['telefone'],
        celular=dados.get('celular'),
        rua=dados['rua'],
        numero=dados['numero'],
        complemento=dados.get('complemento'),
        bairro=dados['bairro'],
        cep=dados['cep'],
        cidade=dados['cidade'],
        uf=dados['uf'],
        criado_em=datetime.utcnow()
    )
    db.add(pj)
    try:
        db.commit()
        db.refresh(pj)
    except Exception as e:
        print(f"[LOG PJ] Erro ao cadastrar PJ: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade ao cadastrar PJ")
    return {"msg": "Pessoa Jurídica cadastrada com sucesso", "id": pj.id}

def validar_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    def calc_digito(cnpj, peso):
        soma = sum(int(a) * b for a, b in zip(cnpj, peso))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)
    peso1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    peso2 = [6] + peso1
    dig1 = calc_digito(cnpj[:12], peso1)
    dig2 = calc_digito(cnpj[:12] + dig1, peso2)
    return cnpj[-2:] == dig1 + dig2

@router.get("/validar-cnpj/{cnpj}")
def validar_cnpj_endpoint(cnpj: str, db: Session = Depends(get_db)):
    if not validar_cnpj(cnpj):
        return {"valido": False, "motivo": "CNPJ inválido"}
    existe = db.query(PessoaJuridica).filter(PessoaJuridica.cnpj == cnpj).first()
    if existe:
        return {"valido": False, "motivo": "CNPJ já cadastrado"}
    return {"valido": True}
