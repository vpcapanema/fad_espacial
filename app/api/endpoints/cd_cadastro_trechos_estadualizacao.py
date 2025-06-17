from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.cd_pessoa_juridica import PessoaJuridica
from app.models.cd_pessoa_fisica import PessoaFisica
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Página de cadastro de trecho (interface HTML)
@router.get("/cadastro-interessado-trecho")
def interessado_trecho(request: Request, db: Session = Depends(get_db)):
    pfs = db.query(PessoaFisica).all()
    pjs = db.query(PessoaJuridica).all()
    return templates.TemplateResponse("cd_trecho.html", {
        "request": request,
        "pfs": pfs,
        "pjs": pjs
    })

# 🔄 Endpoint JSON para atualizar lista de PJs
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

# 🔄 Endpoint JSON para atualizar lista de PFs
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

# 🔄 Endpoint JSON para atualizar lista de Trechos
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

# Endpoint para cadastrar trecho rodoviário
@router.post("/cadastro/trecho")
def cadastrar_trecho(request: Request, db: Session = Depends(get_db)):
    dados = request.form()
    print(f"[LOG TRECHO] Recebida requisição para cadastrar trecho rodoviário: {dados}")

    # Validação simples dos dados
    campos_obrigatorios = ["codigo", "denominacao", "municipio"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            print(f"[LOG TRECHO] Campo obrigatório ausente: {campo}")
            return {"erro": f"Campo obrigatório ausente: {campo}"}, 400

    # Verifica se o trecho já está cadastrado
    trecho_existente = db.query(TrechoEstadualizacao).filter_by(codigo=dados["codigo"]).first()
    if trecho_existente:
        print("[LOG TRECHO] Código de trecho já cadastrado")
        return {"erro": "Código de trecho já cadastrado"}, 400

    # Cadastra o novo trecho
    try:
        novo_trecho = TrechoEstadualizacao(**dados)
        db.add(novo_trecho)
        db.commit()
        db.refresh(novo_trecho)
        print(f"[LOG TRECHO] Trecho rodoviário cadastrado com sucesso: {novo_trecho.id}")
        return {"mensagem": "Trecho rodoviário cadastrado com sucesso", "id": novo_trecho.id}, 201
    except Exception as e:
        print(f"[LOG TRECHO] Erro ao cadastrar trecho rodoviário: {e}")
        return {"erro": "Erro ao cadastrar trecho rodoviário"}, 500
