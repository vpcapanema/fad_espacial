from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session
from app.database.base import Base
from datetime import datetime

class PessoaJuridica(Base):
    __tablename__ = "pessoa_juridica"
    __table_args__ = {"schema": "Cadastro"}

    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String, nullable=False)
    cnpj = Column(String, nullable=False, unique=True)
    nome_fantasia = Column(String, nullable=True)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    rua = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    complemento = Column(String, nullable=True)
    bairro = Column(String, nullable=False)
    cep = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    uf = Column(String, nullable=False)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    projetos = relationship(
        "Projeto",
        back_populates="pessoa_juridica",
        primaryjoin="PessoaJuridica.id == Projeto.pessoa_juridica_id"
    )

class PessoaJuridicaAuditoria(Base):
    __tablename__ = "pessoa_juridica_auditoria"
    __table_args__ = {"schema": "Cadastro"}

    id = Column(Integer, primary_key=True, index=True)
    pessoa_juridica_id = Column(Integer, nullable=False)
    campo = Column(String, nullable=False)
    valor_antigo = Column(String, nullable=True)
    valor_novo = Column(String, nullable=True)
    alterado_por = Column(String, nullable=True)  # id ou nome do usuário
    alterado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

def registrar_auditoria_pessoa_juridica(db: Session, pj_antiga: PessoaJuridica, pj_nova: PessoaJuridica, usuario: str):
    """
    Registra na tabela de auditoria todas as alterações feitas em um registro de PessoaJuridica.
    :param db: sessão do banco
    :param pj_antiga: objeto PessoaJuridica antes da edição
    :param pj_nova: objeto PessoaJuridica após a edição
    :param usuario: identificador do usuário que fez a alteração
    """
    campos = [
        'razao_social', 'cnpj', 'nome_fantasia', 'email', 'telefone', 'celular',
        'rua', 'numero', 'bairro', 'cep', 'cidade', 'uf', 'complemento'
    ]
    for campo in campos:
        valor_antigo = getattr(pj_antiga, campo)
        valor_novo = getattr(pj_nova, campo)
        if valor_antigo != valor_novo:
            auditoria = PessoaJuridicaAuditoria(
                pessoa_juridica_id=pj_antiga.id,
                campo=campo,
                valor_antigo=str(valor_antigo) if valor_antigo is not None else None,
                valor_novo=str(valor_novo) if valor_novo is not None else None,
                alterado_por=usuario
            )
            db.add(auditoria)
    db.commit()
