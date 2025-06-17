"""
Serviço de Geração e Controle de Formulários HTML de Cadastro de Usuário
Responsável por:
- Geração de formulários HTML a partir do template
- Controle de versões dos formulários 
- Sincronização com dados do banco
- Gestão de diretórios por usuário
- Suporte para múltiplos tipos de usuário por CPF (master, coordenador, analista)
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from jinja2 import Environment, FileSystemLoader

from app.models.cd_usuario_sistema import UsuarioSistema

logger = logging.getLogger(__name__)

class FormularioService:
    def __init__(self):
        # Diretório base conforme especificação
        self.base_dir = Path("c:/Users/vinic/fad-geo/formularios_cadastro_usuarios")
        self.template_dir = Path("c:/Users/vinic/fad-geo/app/templates/formularios_cadastro_usuarios")
        self.template_file = "cadastro_usuario_template.html"
        
        # Cria diretório base se não existir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Configura Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        
    def _extrair_usuario_email(self, email_institucional: str) -> str:
        """Extrai o nome de usuário do email institucional (parte antes do @)"""
        if not email_institucional or '@' not in email_institucional:
            raise ValueError("Email institucional inválido para extrair nome de usuário")
        return email_institucional.split('@')[0]
    
    def _criar_diretorio_usuario(self, email_institucional: str, data_criacao: datetime = None) -> Path:
        """
        Cria estrutura de diretórios para o usuário conforme especificação:
        - Pasta principal: [usuario_email]_[data] 
        - Exemplo: bdalves_20250611
        """
        if data_criacao is None:
            data_criacao = datetime.now()
            
        usuario_nome = self._extrair_usuario_email(email_institucional)
        data_str = data_criacao.strftime("%Y%m%d")
        
        # Nome do diretório principal do usuário
        nome_pasta_usuario = f"{usuario_nome}_{data_str}"
        user_dir = self.base_dir / nome_pasta_usuario
        
        # Cria o diretório se não existir
        user_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Diretório do usuário criado/verificado: {user_dir}")
        return user_dir
    
    def _criar_subpasta_tipo(self, user_dir: Path, tipo_usuario: str) -> Path:
        """
        Cria subpasta para o tipo de usuário dentro do diretório principal
        - Exemplo: tipo_coordenador, tipo_analista, tipo_master
        """
        nome_subpasta = f"tipo_{tipo_usuario}"
        tipo_dir = user_dir / nome_subpasta
        
        # Cria a subpasta se não existir
        tipo_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Subpasta do tipo criada/verificada: {tipo_dir}")
        return tipo_dir
        
    def _obter_proxima_versao(self, tipo_dir: Path, usuario_id: int, tipo_usuario: str) -> int:
        """
        Obtém a próxima versão do formulário analisando os arquivos existentes na pasta
        Analisa os arquivos que seguem o padrão: [usuario_id]_[tipo]_[data]_v[versao].html
        """
        try:
            # Lista todos os arquivos HTML na pasta do tipo
            pattern = f"{usuario_id}_{tipo_usuario}_*_v*.html"
            arquivos = list(tipo_dir.glob(pattern))
            
            if not arquivos:
                return 1  # Primeira versão
            
            # Extrai os números de versão dos arquivos existentes
            versoes = []
            for arquivo in arquivos:
                nome = arquivo.stem  # Nome sem extensão
                if '_v' in nome:
                    try:
                        versao_str = nome.split('_v')[-1]
                        versao = int(versao_str)
                        versoes.append(versao)
                    except ValueError:
                        continue
            
            # Retorna a próxima versão
            return max(versoes) + 1 if versoes else 1
            
        except Exception as e:
            logger.error(f"Erro ao obter próxima versão: {e}")
            return 1
    
    def _desativar_versoes_antigas(self, db: Session, usuario_id: int, tipo_usuario: str) -> None:
        """Desativa versões antigas do formulário para o tipo específico, mantendo apenas a mais recente ativa"""
        try:
            db.execute(
                text("""
                UPDATE formularios_usuario 
                SET ativo = FALSE 
                WHERE usuario_id = :usuario_id 
                  AND arquivo_nome LIKE :pattern
                  AND ativo = TRUE
                """),
                {
                    "usuario_id": usuario_id, 
                    "pattern": f"%{tipo_usuario}%"
                }            )
            db.commit()
        except Exception as e:
            logger.error(f"Erro ao desativar versões antigas: {e}")
            db.rollback()
    
    def gerar_formulario_html(self, db: Session, usuario_id: int) -> str:
        """
        Gera formulário HTML para o usuário seguindo as especificações:
        1. Cria pasta: [usuario_email]_[data] em formularios_cadastro_usuarios/
        2. Cria subpasta: tipo_[tipo_usuario]
        3. Gera HTML a partir do template com dados do banco
        4. Salva como: [usuario_id]_[tipo]_[data]_v[versao].html
        
        Retorna o caminho completo do arquivo HTML gerado
        """
        try:
            logger.info(f"🔧 Iniciando geração de formulário HTML para usuário {usuario_id}")
            
            # 1. Busca dados do usuário no banco
            usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
            if not usuario:
                raise Exception(f"Usuário {usuario_id} não encontrado no banco de dados")
              # Valida se tem email institucional
            if not usuario.email_institucional:
                raise Exception(f"Usuário {usuario_id} não possui email institucional cadastrado")
            
            logger.info(f"📋 Dados do usuário carregados - ID: {usuario.id}, Tipo: {usuario.tipo}, Email: {usuario.email_institucional}")
            
            # 2. Cria estrutura de diretórios conforme especificação
            # Pasta principal: [usuario_email]_[data]
            user_dir = self._criar_diretorio_usuario(usuario.email_institucional)
            
            # Subpasta: tipo_[tipo_usuario]
            tipo_dir = self._criar_subpasta_tipo(user_dir, usuario.tipo)
            
            # 3. Obtém próxima versão do formulário
            proxima_versao = self._obter_proxima_versao(tipo_dir, usuario.id, usuario.tipo)
              # 4. Prepara dados para o template (APENAS dados da tabela usuario_sistema)
            dados_template = {
                'usuario': usuario,
                'data_geracao': datetime.now()
            }
            
            logger.info(f"📄 Carregando template de: {self.template_dir}/{self.template_file}")
            
            # 5. Carrega e renderiza o template
            template = self.jinja_env.get_template(self.template_file)
            html_content = template.render(**dados_template)
            
            logger.info(f"✅ Template renderizado com sucesso - Tamanho: {len(html_content)} caracteres")
            
            # 6. Define nome do arquivo conforme especificação: [usuario_id]_[tipo]_[data]_v[versao].html
            data_hoje = datetime.now().strftime("%Y%m%d")
            nome_arquivo = f"{usuario.id}_{usuario.tipo}_{data_hoje}_v{proxima_versao}.html"
            caminho_arquivo = tipo_dir / nome_arquivo
              # 7. Salva o arquivo HTML
            logger.info(f"💾 Salvando arquivo HTML em: {caminho_arquivo}")
            
            try:
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"✅ Arquivo HTML salvo com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar arquivo HTML: {e}")
                raise Exception(f"Falha ao salvar arquivo HTML: {e}")
            
            # Verifica se o arquivo foi criado
            if not caminho_arquivo.exists():
                logger.error(f"❌ Arquivo não foi criado: {caminho_arquivo}")
                raise Exception(f"Falha ao criar arquivo HTML: {caminho_arquivo}")
            
            # Verifica se o arquivo tem conteúdo
            tamanho_arquivo = caminho_arquivo.stat().st_size
            if tamanho_arquivo == 0:
                logger.error(f"❌ Arquivo criado mas está vazio: {caminho_arquivo}")
                raise Exception(f"Arquivo HTML criado mas está vazio: {caminho_arquivo}")
                
            logger.info(f"✅ Arquivo HTML verificado: {tamanho_arquivo} bytes")
            
            tamanho_arquivo = caminho_arquivo.stat().st_size
            logger.info(f"✅ Formulário HTML salvo com sucesso:")
            logger.info(f"   📁 Caminho: {caminho_arquivo}")
            logger.info(f"   📊 Tamanho: {tamanho_arquivo} bytes")
            logger.info(f"   🔢 Versão: {proxima_versao}")
            
            # 8. Registra na tabela de controle (opcional, para auditoria)
            try:
                db.execute(
                    text("""
                    INSERT INTO formularios_usuario (
                        usuario_id, arquivo_nome, caminho_completo, 
                        data_geracao, versao, ativo, tamanho_arquivo, status,
                        hash_conteudo, observacoes
                    ) VALUES (
                        :usuario_id, :arquivo_nome, :caminho_completo,
                        :data_geracao, :versao, :ativo, :tamanho_arquivo, :status,
                        :hash_conteudo, :observacoes
                    )
                    """),
                    {
                        'usuario_id': usuario.id,
                        'arquivo_nome': nome_arquivo,
                        'caminho_completo': str(caminho_arquivo),
                        'data_geracao': datetime.now(),
                        'versao': proxima_versao,
                        'ativo': True,
                        'tamanho_arquivo': tamanho_arquivo,
                        'status': 'ativo',
                        'hash_conteudo': f"html_{usuario.id}_{usuario.tipo}_{data_hoje}_v{proxima_versao}",
                        'observacoes': f"Formulário HTML gerado automaticamente para usuário {usuario.tipo} (Email: {usuario.email_institucional})"
                    }
                )
                db.commit()
                logger.info(f"📝 Registro de auditoria criado na tabela formularios_usuario")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao registrar na tabela de auditoria (não crítico): {e}")
                # Não interrompe o processo se falhar o registro de auditoria
            
            # Retorna o caminho completo do arquivo gerado
            return str(caminho_arquivo)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar formulário HTML para usuário {usuario_id}: {e}")
            logger.error(f"❌ Tipo do erro: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
    def atualizar_formulario_usuario(self, db: Session, usuario_id: int) -> str:
        """
        Atualiza o formulário de um usuário específico com dados atuais do banco
        Usado quando dados do usuário são modificados
        """
        try:
            logger.info(f"🔄 Atualizando formulário do usuário {usuario_id}")
            return self.gerar_formulario_html(db, usuario_id)
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar formulário do usuário {usuario_id}: {e}")
            raise

# Instância global do serviço
formulario_service = FormularioService()
