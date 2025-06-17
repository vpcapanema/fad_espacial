from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, Session
from app.database.base import Base
from datetime import datetime

class UsuarioSistema(Base):
    __tablename__ = "usuario_sistema"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('analista', 'coordenador', 'master')",
            name="check_tipo_usuario_valido"
        ),
        {"schema": "Cadastro"}  # ← precisa ser o último item
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False)  # unique removido para permitir a restrição composta
    email = Column(String, nullable=False)
    telefone = Column(String)
    pessoa_fisica_id = Column(Integer, ForeignKey("Cadastro.pessoa_fisica.id"), nullable=True)
    instituicao = Column(String, nullable=True)
    tipo_lotacao = Column(String, nullable=True)
    email_institucional = Column(String, nullable=True)
    telefone_institucional = Column(String, nullable=True)
    ramal = Column(String, nullable=True)
    sede_hierarquia = Column(String, nullable=True)
    sede_assistencia_direta = Column(String, nullable=True)  # nova coluna para Assistência Direta
    sede_diretoria = Column(String, nullable=True)  # nova coluna para Diretoria
    sede_coordenadoria_geral = Column(String, nullable=True)  # nova coluna para Coordenadoria Geral
    sede_coordenadoria = Column(String, nullable=True)
    sede_assistencia = Column(String, nullable=True)
    regional_nome = Column(String, nullable=True)
    regional_coordenadoria = Column(String, nullable=True)
    regional_setor = Column(String, nullable=True)
    senha_hash = Column(String, nullable=False)
    tipo = Column(String, nullable=False, default="analista")
    criado_em = Column(DateTime, default=datetime.utcnow)
    aprovado_em = Column(DateTime, nullable=True)
    aprovador_id = Column(Integer, ForeignKey("Cadastro.usuario_sistema.id"), nullable=True)
    status = Column(String, default="aguardando aprovacao")
    ativo = Column(Boolean, default=True)

    pessoa_fisica = relationship(
        "PessoaFisica",
        back_populates="usuarios",
        primaryjoin="UsuarioSistema.pessoa_fisica_id == PessoaFisica.id"
    )
    aprovador = relationship(
        "UsuarioSistema",
        remote_side=[id],
        primaryjoin="UsuarioSistema.aprovador_id == UsuarioSistema.id"
    )

    recuperacoes_senha = relationship(
        "RecuperacaoSenha",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

class UsuarioSistemaAuditoria(Base):
    __tablename__ = "usuario_sistema_auditoria"
    __table_args__ = {"schema": "Cadastro"}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    campo = Column(String, nullable=False)
    valor_antigo = Column(String, nullable=True)
    valor_novo = Column(String, nullable=True)
    alterado_por = Column(String, nullable=True)  # id ou nome do usuário
    alterado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

def registrar_auditoria_usuario_sistema(db: Session, usuario_antigo: UsuarioSistema, usuario_novo: UsuarioSistema, usuario: str):
    campos = [
        'nome', 'cpf', 'email', 'telefone', 'pessoa_fisica_id', 'instituicao', 'tipo_lotacao',
        'email_institucional', 'telefone_institucional', 'ramal', 'sede_hierarquia', 'sede_coordenadoria',
        'sede_assistencia', 'regional_nome', 'regional_coordenadoria', 'regional_setor',
        'tipo', 'status', 'ativo'
    ]
    for campo in campos:
        valor_antigo = getattr(usuario_antigo, campo)
        valor_novo = getattr(usuario_novo, campo)
        if valor_antigo != valor_novo:
            auditoria = UsuarioSistemaAuditoria(
                usuario_id=usuario_antigo.id,
                campo=campo,
                valor_antigo=str(valor_antigo) if valor_antigo is not None else None,
                valor_novo=str(valor_novo) if valor_novo is not None else None,
                alterado_por=usuario
            )
            db.add(auditoria)
    db.commit()

