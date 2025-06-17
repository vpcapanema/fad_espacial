from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from app.database.base import Base

class PessoaFisica(Base):
    __tablename__ = "pessoa_fisica"
    __table_args__ = {"schema": "Cadastro"}

    id = Column(Integer, primary_key=True, index=True)  # Chave primária única
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)  # CPF único
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    logradouro = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    complemento = Column(String, nullable=True)
    cep = Column(String, nullable=False)
    bairro = Column(String, nullable=False)
    municipio = Column(String, nullable=False)
    uf = Column(String, nullable=False)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuarios = relationship(
        "UsuarioSistema",
        back_populates="pessoa_fisica",
        primaryjoin="PessoaFisica.id == UsuarioSistema.pessoa_fisica_id"
    )

class PessoaFisicaAuditoria(Base):
    __tablename__ = "pessoa_fisica_auditoria"
    __table_args__ = {"schema": "Cadastro"}

    id = Column(Integer, primary_key=True, index=True)
    pessoa_fisica_id = Column(Integer, nullable=False)
    campo = Column(String, nullable=False)
    valor_antigo = Column(String, nullable=True)
    valor_novo = Column(String, nullable=True)
    alterado_por = Column(String, nullable=True)  # id ou nome do usuário
    alterado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

def registrar_auditoria_pessoa_fisica(db: Session, pessoa_antiga: PessoaFisica, pessoa_nova: PessoaFisica, usuario: str):
    """
    Registra na tabela de auditoria todas as alterações feitas em um registro de PessoaFisica.
    :param db: sessão do banco
    :param pessoa_antiga: objeto PessoaFisica antes da edição
    :param pessoa_nova: objeto PessoaFisica após a edição
    :param usuario: identificador do usuário que fez a alteração
    """
    campos = [
        'nome', 'cpf', 'email', 'telefone', 'rua', 'numero', 'complemento', 'bairro',
        'cep', 'cidade', 'uf'
    ]
    for campo in campos:
        valor_antigo = getattr(pessoa_antiga, campo)
        valor_novo = getattr(pessoa_nova, campo)
        if valor_antigo != valor_novo:
            auditoria = PessoaFisicaAuditoria(
                pessoa_fisica_id=pessoa_antiga.id,
                campo=campo,
                valor_antigo=str(valor_antigo) if valor_antigo is not None else None,
                valor_novo=str(valor_novo) if valor_novo is not None else None,
                alterado_por=usuario
            )
            db.add(auditoria)
    db.commit()
