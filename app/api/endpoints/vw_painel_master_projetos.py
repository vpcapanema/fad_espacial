from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db

router = APIRouter(
    prefix='/painel',
    tags=['Painel do Master']
)

@router.get('/projetos')
def listar_todos_os_projetos(db: Session = Depends(get_db)):
    query = '''
        SELECT 
            p.id AS "Id",
            p.nome AS "Nome",
            COALESCE(pj.razao_social, pf.nome) AS "Interessado",
            COALESCE(pj.cnpj, '') AS "CNPJ",
            COALESCE(rep.nome, '') AS "Representante legal",
            COALESCE(rep_pf.cpf, '') AS "CPF",
            COALESCE(rep.email, pf.email, pj.email) AS "E-mail",
            COALESCE(rep.telefone, pf.telefone, pj.telefone) AS "Telefone",
            COALESCE(p.trecho, '') AS "Trecho",
            COALESCE(p.municipio_uf, '') AS "Município/UF",
            COALESCE(p.extensao::text, '') AS "Extensão",
            COALESCE(p.extensao_calculada::text, '') AS "Extensão calculada",
            COALESCE(analista.nome, '') AS "Analista responsável",
            COALESCE(p.criado_em::text, '') AS "Criado em",
            COALESCE(p.status, 'rascunho') AS "Situação do projeto",
            COALESCE(p.status_upload, '') AS "Situação do upload",
            COALESCE(p.status_geometria, '') AS "Situaçao da geometria",
            COALESCE(p.validada_em::text, '') AS "Validada em",
            COALESCE(p.status_ca, '') AS "Situaçao da conformidade ambiental",
            COALESCE(p.ca_aprovada_em::text, '') AS "CA aprovada em",
            COALESCE(p.status_ifm, '') AS "Situação do IFM",
            COALESCE(p.ifm_trecho, '') AS "IFM trecho",
            COALESCE(p.ifm_aprovado_em::text, '') AS "IFM aprovado em",
            COALESCE(p.status_ifs, '') AS "Situação do IFS",
            COALESCE(p.ifs_trecho, '') AS "IFS trecho",
            COALESCE(p.ifs_aprovado_em::text, '') AS "IFS aprovado em",
            COALESCE(p.status_iqi, '') AS "Situação do IQI",
            COALESCE(p.iqi_trecho, '') AS "IQI trecho",
            COALESCE(p.iqi_aprovado_em::text, '') AS "IQI aprovado em"
        FROM projeto p
        LEFT JOIN "Cadastro".pessoa_juridica pj ON pj.id = p.pessoa_juridica_id
        LEFT JOIN "Cadastro".pessoa_fisica pf ON pf.id = p.pessoa_fisica_id
        LEFT JOIN "Cadastro".usuario_sistema rep ON rep.id = p.representante_id
        LEFT JOIN "Cadastro".pessoa_fisica rep_pf ON rep_pf.id = rep.pessoa_fisica_id
        LEFT JOIN "Cadastro".usuario_sistema analista ON analista.id = p.analista_id
        ORDER BY p.id DESC
    '''
    projetos = db.execute(text(query)).fetchall()
    return [dict(row._mapping) for row in projetos]