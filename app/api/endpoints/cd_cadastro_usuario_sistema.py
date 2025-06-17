from fastapi import APIRouter, Request, Form, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from app.database.session import get_db
from app.core.jinja import templates
from app.models.cd_usuario_sistema import UsuarioSistema
        
from app.models.cd_pessoa_fisica import PessoaFisica
from app.schemas.usuario import UsuarioCreate
from passlib.hash import bcrypt
import re
import logging
import os
import pdfkit
import asyncio

# Configuração básica de logging para debug detalhado
logging.basicConfig(level=logging.INFO, format='[FAD DEBUG] %(asctime)s %(levelname)s %(message)s')

def limpar_formatacao_telefone(telefone):
    """
    Remove toda formatação de telefone, mantendo apenas números
    """
    if not telefone:
        return None
    return re.sub(r"[^\d]", "", str(telefone))

def limpar_formatacao_cpf(cpf):
    """
    Remove toda formatação de CPF, mantendo apenas números
    """
    if not cpf:
        return None
    return re.sub(r"[^\d]", "", str(cpf))

def log_requisicao(request: Request, etapa: str, info_extra: str = ""):
    logging.info(f"{etapa} | {request.method} {request.url.path} | IP: {request.client.host} | {info_extra}")

# ✅ Padrão de roteador aplicado
router = APIRouter(
    tags=['Cadastro de Usuário']
)

# ===============================
# Endpoint JSON para cadastro via JavaScript
# ===============================
@router.post("/cadastrar-usuario")
async def cadastrar_usuario_json(request: Request, usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Endpoint para cadastro de usuário via JSON (usado pelo JavaScript do frontend)
    """
    from datetime import datetime
    import os
    
    log_requisicao(request, "INÍCIO", f"Cadastro JSON para: {usuario_data.nome}")
    
    try:
        # Verifica se o tipo de usuário é 'master'
        if usuario_data.tipo == "master":
            raise HTTPException(
                status_code=400,
                detail="O tipo de usuário 'master' só pode ser criado pela equipe técnica da FAD."
            )
        
        # ✅ LIMPEZA DE FORMATAÇÃO - CPF e TELEFONES
        cpf_limpo = limpar_formatacao_cpf(usuario_data.cpf)
        telefone_pessoal_limpo = limpar_formatacao_telefone(usuario_data.telefone)
        telefone_institucional_limpo = limpar_formatacao_telefone(usuario_data.telefone_institucional)
        
        # Log para debug
        logging.info(f"🔍 Limpeza de dados:")
        logging.info(f"  CPF original: '{usuario_data.cpf}' -> limpo: '{cpf_limpo}'")
        logging.info(f"  Tel. pessoal original: '{usuario_data.telefone}' -> limpo: '{telefone_pessoal_limpo}'")
        logging.info(f"  Tel. institucional original: '{usuario_data.telefone_institucional}' -> limpo: '{telefone_institucional_limpo}'")
        
        # ✅ VALIDAÇÃO DE UNICIDADE: CPF + TIPO
        # Verifica se já existe um usuário com a mesma combinação de CPF e tipo
        usuario_existente = db.query(UsuarioSistema).filter(
            UsuarioSistema.cpf == cpf_limpo,
            UsuarioSistema.tipo == usuario_data.tipo
        ).first()
        
        if usuario_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um usuário {usuario_data.tipo} cadastrado com este CPF."
            )
        
        # ✅ VALIDAÇÃO DE LIMITE: Máximo 3 tipos por CPF (master, coordenador, analista)
        usuarios_mesmo_cpf = db.query(UsuarioSistema).filter(UsuarioSistema.cpf == cpf_limpo).all()
        if len(usuarios_mesmo_cpf) >= 3:
            tipos_existentes = [u.tipo for u in usuarios_mesmo_cpf]
            logging.info(f"🔍 CPF {cpf_limpo} já possui {len(usuarios_mesmo_cpf)} usuários: {tipos_existentes}")
            raise HTTPException(
                status_code=400,
                detail=f"Este CPF já está cadastrado para os três tipos de usuário permitidos: {', '.join(tipos_existentes)}."
            )
        
        # Validações de formato usando dados limpos
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        telefone_regex = r"^\d{10,11}$"
        cpf_regex = r"^\d{11}$"
        ramal_regex = r"^\d{4,}$"
        
        # Validação obrigatória: email pessoal
        if not re.match(email_regex, usuario_data.email):
            raise HTTPException(status_code=400, detail="E-mail pessoal inválido.")
        
        # Validação obrigatória: CPF (agora usando dados limpos)
        if not re.match(cpf_regex, cpf_limpo):
            raise HTTPException(status_code=400, detail="CPF inválido.")
        
        # Validações opcionais - apenas se campos estiverem preenchidos
        if usuario_data.email_institucional and not re.match(email_regex, usuario_data.email_institucional):
            raise HTTPException(status_code=400, detail="E-mail institucional inválido.")
        
        # ✅ Validação de telefones usando dados limpos    
        if telefone_pessoal_limpo and not re.match(telefone_regex, telefone_pessoal_limpo):
            raise HTTPException(status_code=400, detail="Telefone pessoal inválido. Deve conter 10 ou 11 dígitos.")
            
        if telefone_institucional_limpo and not re.match(telefone_regex, telefone_institucional_limpo):
            raise HTTPException(status_code=400, detail="Telefone institucional inválido. Deve conter 10 ou 11 dígitos.")
            
        if usuario_data.ramal and not re.match(ramal_regex, usuario_data.ramal):
            raise HTTPException(status_code=400, detail="Ramal inválido.")
        
        # ✅ Criação do novo usuário com dados limpos
        novo_usuario = UsuarioSistema(
            nome=usuario_data.nome,
            cpf=cpf_limpo,  # ✅ CPF sem formatação
            email=usuario_data.email,
            telefone=telefone_pessoal_limpo,  # ✅ Telefone sem formatação
            senha_hash=bcrypt.hash(usuario_data.senha),
            tipo=usuario_data.tipo,
            pessoa_fisica_id=getattr(usuario_data, 'pessoa_fisica_id', None),
            status="aguardando aprovação",
            ativo=False,
            instituicao=usuario_data.instituicao,
            tipo_lotacao=usuario_data.tipo_lotacao,
            email_institucional=usuario_data.email_institucional,
            telefone_institucional=telefone_institucional_limpo,  # ✅ Telefone sem formatação
            ramal=usuario_data.ramal,
            sede_hierarquia=getattr(usuario_data, 'sede_hierarquia', None),
            sede_assistencia_direta=getattr(usuario_data, 'sede_assistencia_direta', None),
            sede_diretoria=usuario_data.sede_diretoria,
            sede_coordenadoria_geral=usuario_data.sede_coordenadoria_geral,            sede_coordenadoria=getattr(usuario_data, 'sede_coordenadoria', None),
            sede_assistencia=getattr(usuario_data, 'sede_assistencia', None),
            regional_nome=getattr(usuario_data, 'regional_nome', None),
            regional_coordenadoria=getattr(usuario_data, 'regional_coordenadoria', None),
            regional_setor=getattr(usuario_data, 'regional_setor', None)
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        logging.info(f"✅ Usuário criado com ID {novo_usuario.id} - dados salvos no banco:")
        logging.info(f"  CPF no banco: '{novo_usuario.cpf}'")
        logging.info(f"  Tel. pessoal no banco: '{novo_usuario.telefone}'")
        logging.info(f"  Tel. institucional no banco: '{novo_usuario.telefone_institucional}'")        # ✅ GERAÇÃO DO FORMULÁRIO HTML COM SISTEMA DE VERSIONAMENTO
        from app.services.formulario_service import formulario_service
        
        # Inicializa variáveis para garantir que estejam sempre disponíveis
        formulario_html = None
        caminho_html = None
        
        try:
            logging.info(f"🔧 Iniciando geração de formulário HTML para usuário {novo_usuario.id} tipo {novo_usuario.tipo}")
            logging.info(f"🔧 Dados do usuário para formulário:")
            logging.info(f"   Nome: {novo_usuario.nome}")
            logging.info(f"   Email: {novo_usuario.email}")
            logging.info(f"   Tipo: {novo_usuario.tipo}")
            logging.info(f"   Instituição: {novo_usuario.instituicao}")
              # Gera formulário HTML baseado no template com dados do banco
            # Nova implementação: retorna diretamente o caminho do arquivo salvo
            formulario_html = formulario_service.gerar_formulario_html(db, novo_usuario.id)
            
            logging.info(f"🔧 Retorno do FormularioService: {formulario_html}")
            logging.info(f"🔧 Tipo do retorno: {type(formulario_html)}")
            
            # Verificações de segurança
            if formulario_html is None:
                raise Exception("FormularioService retornou None - falha na geração")
                
            if not isinstance(formulario_html, str):
                raise Exception(f"FormularioService retornou tipo inválido: {type(formulario_html)}")
                
            if not formulario_html.strip():
                raise Exception("FormularioService retornou string vazia")
                
            # Converte para Path e verifica existência
            from pathlib import Path
            arquivo_formulario = Path(formulario_html)
            
            if not arquivo_formulario.exists():
                raise Exception(f"Arquivo do formulário não foi criado: {formulario_html}")
                
            if not arquivo_formulario.is_file():
                raise Exception(f"Caminho não é um arquivo válido: {formulario_html}")
                
            tamanho_arquivo = arquivo_formulario.stat().st_size
            if tamanho_arquivo == 0:
                raise Exception(f"Arquivo do formulário está vazio: {formulario_html}")
                
            logging.info(f"✅ Formulário HTML gerado com sucesso:")
            logging.info(f"   📁 Caminho: {formulario_html}")
            logging.info(f"   📄 Tamanho: {tamanho_arquivo} bytes")
            logging.info(f"   ✓ Arquivo existe e é válido")
            
            # Usa o formulário HTML gerado como base para o PDF
            caminho_html = formulario_html
            
        except Exception as e:
            logging.error(f"❌ ERRO DETALHADO na geração do formulário HTML:")
            logging.error(f"   Erro: {e}")
            logging.error(f"   Tipo do erro: {type(e)}")
            logging.error(f"   Usuário ID: {novo_usuario.id}")
            logging.error(f"   formulario_html recebido: {formulario_html}")
            
            import traceback
            logging.error(f"   Traceback completo:")
            for linha in traceback.format_exc().split('\n'):
                if linha.strip():
                    logging.error(f"     {linha}")
                      # Define formulario_html como None para evitar problemas downstream
            formulario_html = None
            
            # NÃO FALHA O PROCESSO - continua sem o formulário HTML
            logging.warning("⚠️ Continuando processo sem formulário HTML...")
            
            # Define caminho_html como None para evitar erro na geração do PDF
            caminho_html = None
        
        # Configuração do diretório de PDF: mesmo diretório do formulário HTML
        dir_html = os.path.dirname(caminho_html) if caminho_html else os.getcwd()
        os.makedirs(dir_html, exist_ok=True)
        # Nome do arquivo PDF baseado no formulário HTML
        nome_arquivo_html = os.path.basename(formulario_html) if formulario_html else f"cadastro_usuario_{novo_usuario.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_v1.html"
        nome_arquivo_pdf = nome_arquivo_html.replace('.html', '.pdf')
        # Gera PDF no mesmo diretório do HTML
        caminho_pdf = os.path.join(dir_html, nome_arquivo_pdf)
        
        pdf_gerado = False
        
        try:
            # Tenta gerar PDF com pdfkit/wkhtmltopdf
            import pdfkit
            
            # ========================================
            # CONFIGURAÇÃO OTIMIZADA PARA FIDELIDADE VISUAL
            # ========================================
            
            # Configuração específica do wkhtmltopdf (se disponível)
            config = pdfkit.configuration()  # Pode especificar caminho se necessário
            
            # Opções avançadas para máxima fidelidade visual
            options = {
                # === CONFIGURAÇÕES DE PÁGINA ===
                'page-size': 'A4',
                'orientation': 'Portrait',
                'margin-top': '10mm',
                'margin-right': '10mm', 
                'margin-bottom': '10mm',
                'margin-left': '10mm',
                
                # === RENDERIZAÇÃO E QUALIDADE ===
                'dpi': 300,  # Alta resolução para texto nítido
                'image-dpi': 300,  # Resolução alta para imagens
                'image-quality': 100,  # Qualidade máxima de imagem
                'print-media-type': None,  # Usa media print CSS
                'disable-smart-shrinking': None,  # Evita redimensionamento automático
                'zoom': 1.0,  # Zoom 100% para fidelidade exata
                
                # === FONTS E TEXTO ===
                'encoding': 'UTF-8',
                'minimum-font-size': 8,  # Mínimo para legibilidade
                
                # === JAVASCRIPT E CSS ===
                'enable-javascript': None,  # Habilita JS para renderização dinâmica
                'javascript-delay': 1000,  # Aguarda 1s para JS executar
                'no-stop-slow-scripts': None,  # Não para scripts lentos
                'debug-javascript': None,  # Debug de JS se necessário
                
                # === RECURSOS EXTERNOS ===
                'enable-local-file-access': None,  # Acesso a arquivos locais (CSS, imagens)
                'load-error-handling': 'ignore',  # Ignora erros de carregamento
                'load-media-error-handling': 'ignore',  # Ignora erros de mídia
                
                # === FORMATAÇÃO ===
                'disable-external-links': None,  # Remove links externos no PDF
                'no-outline': None,  # Remove outline/bookmark automático
                'quiet': None,  # Execução silenciosa
                
                # === CACHE E PERFORMANCE ===
                'cache-dir': None,  # Desabilita cache para consistência
                'cookie-jar': None,  # Sem cookies
                
                # === RENDERIZAÇÃO AVANÇADA ===
                'viewport-size': '1280x1024',  # Viewport consistente
                'user-style-sheet': None,  # Sem CSS adicional
                'custom-header': [
                    ('Accept-Encoding', 'gzip')
                ],
                
                # === DEBUGGING (remover em produção) ===
                # 'debug': None,  # Comentado para produção
            }
            
            # Geração do PDF com configuração otimizada
            pdfkit.from_file(caminho_html, caminho_pdf, options=options, configuration=config)
            pdf_gerado = True
            logging.info(f"✅ PDF gerado com wkhtmltopdf (configuração otimizada): {caminho_pdf}")
            
            # Verifica tamanho do arquivo gerado
            if os.path.exists(caminho_pdf):
                tamanho_pdf = os.path.getsize(caminho_pdf)
                logging.info(f"📏 Tamanho do PDF: {tamanho_pdf:,} bytes")
            else:
                raise Exception("PDF não foi criado pelo wkhtmltopdf")
                
        except Exception as e:
            logging.warning(f"⚠️  wkhtmltopdf falhou (tentativa otimizada): {e}")
            logging.info("🔄 Tentando com html2pdf...")
            
            # Fallback: usa html2pdf
            from app.services.email_service import gerar_comprovante_cadastro_pdf_html2pdf
            
            # Gera PDF a partir do HTML já renderizado
            pdf_gerado = gerar_comprovante_cadastro_pdf_html2pdf(caminho_html, caminho_pdf)
            if pdf_gerado:
                logging.info(f"✅ PDF gerado com html2pdf: {caminho_pdf}")
            else:
                logging.error("❌ Falha ao gerar PDF com html2pdf")
        if not pdf_gerado:
            raise HTTPException(
                status_code=500, 
                detail="Erro ao gerar comprovante PDF. Entre em contato com o suporte."
            )
        
        # Envio de email
        from app.services.email_service import email_service
        
        email_enviado = email_service.enviar_email_confirmacao_cadastro(
            destinatario_email=novo_usuario.email_institucional or novo_usuario.email,
            destinatario_nome=novo_usuario.nome,
            comprovante_pdf_path=caminho_pdf,
            dados_cadastro={
                'nome': novo_usuario.nome,
                'cpf': novo_usuario.cpf,
                'tipo': novo_usuario.tipo,
                'email_institucional': novo_usuario.email_institucional,
                'instituicao': novo_usuario.instituicao,
                'status': 'Cadastrado - Aguardando Aprovação'
            },
            ip_origem=request.client.host,
            user_agent=request.headers.get("user-agent", "Desconhecido")
        )
        
        # Registra o formulário HTML na tabela de controle
        try:
            # Registra o formulário HTML gerado
            db.execute(
                text("""
                INSERT INTO formularios_usuario (
                    usuario_id, arquivo_nome, caminho_completo, data_geracao, 
                    versao, ativo, tamanho_arquivo, status, data_envio_email,
                    hash_conteudo, observacoes
                )
                VALUES (
                    :usuario_id, :arquivo_nome, :caminho_completo, :data_geracao, 
                    :versao, :ativo, :tamanho_arquivo, :status, :data_envio_email,
                    :hash_conteudo, :observacoes
                )
                """),                {
                    'usuario_id': novo_usuario.id,
                    'arquivo_nome': os.path.basename(formulario_html) if formulario_html else f"erro_geração_{novo_usuario.id}.html",
                    'caminho_completo': formulario_html,
                    'data_geracao': datetime.now(),
                    'versao': 1,
                    'ativo': True,
                    'tamanho_arquivo': os.path.getsize(formulario_html) if formulario_html and os.path.exists(formulario_html) else 0,
                    'status': 'ativo',
                    'data_envio_email': datetime.now() if email_enviado else None,
                    'hash_conteudo': f"html_{novo_usuario.id}_{novo_usuario.tipo}",
                    'observacoes': f"Formulário HTML gerado automaticamente para usuário {novo_usuario.tipo}"
                }
            )
            
            # Registra também o PDF gerado
            db.execute(
                text("""
                INSERT INTO formularios_usuario (
                    usuario_id, arquivo_nome, caminho_completo, data_geracao, 
                    versao, ativo, tamanho_arquivo, status, data_envio_email,
                    hash_conteudo, observacoes
                )
                VALUES (
                    :usuario_id, :arquivo_nome, :caminho_completo, :data_geracao, 
                    :versao, :ativo, :tamanho_arquivo, :status, :data_envio_email,
                    :hash_conteudo, :observacoes
                )
                """),
                {                    'usuario_id': novo_usuario.id,
                    'arquivo_nome': nome_arquivo_pdf,
                    'caminho_completo': caminho_pdf,
                    'data_geracao': datetime.now(),
                    'versao': 1,
                    'ativo': True,
                    'tamanho_arquivo': os.path.getsize(caminho_pdf) if os.path.exists(caminho_pdf) else 0,
                    'status': 'ativo',
                    'data_envio_email': datetime.now() if email_enviado else None,
                    'hash_conteudo': f"pdf_{novo_usuario.id}_{novo_usuario.tipo}",
                    'observacoes': f"PDF gerado a partir do formulário HTML para usuário {novo_usuario.tipo}"
                }
            )
            db.commit()
            
        except Exception as e:
            logging.error(f"❌ Erro ao registrar formulários na tabela de controle: {e}")
            # Não falha o processo se houver erro apenas no registro
        
        if not email_enviado:
            logging.warning("Falha no envio do email de confirmação de cadastro")
        
        log_requisicao(request, "FIM", f"Usuário {novo_usuario.id} cadastrado com sucesso")
          # Log final das variáveis importantes para debug
        logging.info(f"🔍 VALORES FINAIS ANTES DA RESPOSTA:")
        logging.info(f"   formulario_html: {formulario_html}")
        logging.info(f"   caminho_pdf: {caminho_pdf}")
        logging.info(f"   email_enviado: {email_enviado}")
        logging.info(f"   pdf_gerado: {pdf_gerado}")
        return JSONResponse(
            status_code=201,
            content={
                "id": novo_usuario.id,
                "nome": novo_usuario.nome,
                "status": "Cadastrado com sucesso",
                "email_enviado": email_enviado,
                "comprovante_gerado": pdf_gerado,
                "formulario_html": formulario_html if formulario_html else None,
                "caminho_pdf": caminho_pdf
            }
        )
        
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        log_requisicao(request, "ERRO", f"IntegrityError: {error_msg}")
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao cadastrar: {error_msg}"
        )
    except Exception as e:
        db.rollback()
        log_requisicao(request, "ERRO", f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )

# ===============================
# Endpoint GET para exibir página de cadastro
# ===============================
@router.get("/cadastro-usuario-sistema", response_class=HTMLResponse)
async def exibir_cadastro_usuario(request: Request):
    """
    Endpoint para exibir a página de cadastro de usuário
    """
    log_requisicao(request, "PÁGINA", "Exibindo formulário de cadastro")
    
    return templates.TemplateResponse(
        "cd_cadastro_usuario.html",
        {"request": request}
    )
