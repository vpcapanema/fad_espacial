"""
Serviço de Email para FAD - Sistema de Recuperação de Senha
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import logging
from datetime import datetime

# Importações para geração de PDF alternativa
try:

    import pdfkit
    PDFKIT_DISPONIVEL = True
except ImportError:
    PDFKIT_DISPONIVEL = False

# Configuração do logger
logger = logging.getLogger(__name__)

def gerar_comprovante_cadastro_pdf_html2pdf(caminho_html, caminho_pdf):
    """
    Gera comprovante de cadastro em PDF a partir do HTML usando pdfkit/wkhtmltopdf
    
    Args:
        caminho_html: Caminho do arquivo HTML de origem
        caminho_pdf: Caminho onde salvar o PDF
    
    Returns:
        bool: True se gerado com sucesso, False caso contrário
    """
    if not PDFKIT_DISPONIVEL:
        logger.error("pdfkit/wkhtmltopdf não está disponível para geração de PDF")
        return False
    try:
        options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'dpi': 300,
            'image-dpi': 300,
            'image-quality': 100,
            'print-media-type': None,
            'disable-smart-shrinking': None,
            'zoom': 1.0,
            'encoding': 'UTF-8',
            'minimum-font-size': 8,
            'enable-javascript': None,
            'javascript-delay': 1000,
            'no-stop-slow-scripts': None,
            'enable-local-file-access': None,
            'quiet': None,
        }
        config = pdfkit.configuration()
        pdfkit.from_file(caminho_html, caminho_pdf, options=options, configuration=config)
        logger.info(f"PDF gerado com sucesso usando pdfkit/wkhtmltopdf: {caminho_pdf}")
        return True
    except Exception as e:
        logger.error(f"Erro ao gerar PDF com pdfkit/wkhtmltopdf: {e}")
        return False

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "fadgeoteste@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "fadgeoteste@gmail.com")
        self.from_name = os.getenv("SMTP_FROM_NAME", "FAD - Plataforma de Análise Dinamizada")
        
        # Inicializa monitor de logs
        try:
            from monitorar_emails import email_monitor
            self.monitor = email_monitor
        except ImportError:
            self.monitor = None
            logger.warning("Monitor de emails não disponível")

    def _registrar_log_email(self, tipo_email, destinatario, assunto, status, erro=None, 
                           tamanho_anexo=None, ip_origem=None, user_agent=None, 
                           tempo_processamento_ms=None):
        """Registra log de envio de email"""
        if self.monitor:
            try:
                self.monitor.registrar_envio(
                    tipo_email=tipo_email,
                    destinatario=destinatario,
                    remetente=self.from_email,
                    assunto=assunto,
                    status=status,
                    erro=erro,
                    tamanho_anexo=tamanho_anexo,
                    ip_origem=ip_origem,
                    user_agent=user_agent,
                    tempo_processamento_ms=tempo_processamento_ms
                )
            except Exception as e:
                logger.error(f"Erro ao registrar log de email: {e}")

    def _create_smtp_connection(self):
        """Cria conexão SMTP segura"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except smtplib.SMTPAuthenticationError as e:
            if "Application-specific password required" in str(e):
                logger.error("ERRO: Gmail requer senha de aplicativo!")
            raise e
        except Exception as e:
            logger.error(f"Erro ao conectar SMTP: {e}")
            raise

    def enviar_email_recuperacao_senha(self, destinatario_email, destinatario_nome, 
                                     token_recuperacao, base_url="http://127.0.0.1:8000",
                                     ip_origem=None, user_agent=None):
        """Envia email de recuperação de senha"""
        inicio_tempo = time.time()
        assunto = "FAD - Recuperação de Senha"
        
        try:
            environment = os.getenv("ENVIRONMENT", "development")
            
            # Modo desenvolvimento
            if (environment == "development" or not self.smtp_password or 
                self.smtp_password in ["", "sua_senha_de_app_aqui", "Malditas131533*", "DESENVOLVIMENTO"]):
                
                print("=" * 60)
                print("MODO DESENVOLVIMENTO - EMAIL SIMULADO")
                print("=" * 60)
                print(f"Para: {destinatario_email}")
                print(f"Nome: {destinatario_nome}")
                print(f"Assunto: {assunto}")
                print(f"Link: {base_url}/recuperacao/redefinir/{token_recuperacao}")
                print("=" * 60)
                
                tempo_processamento = int((time.time() - inicio_tempo) * 1000)
                self._registrar_log_email(
                    tipo_email="recuperacao_senha",
                    destinatario=destinatario_email,
                    assunto=assunto,
                    status="simulado_dev",
                    ip_origem=ip_origem,
                    user_agent=user_agent,
                    tempo_processamento_ms=tempo_processamento
                )
                
                return True
            
            # Modo produção
            link_recuperacao = f"{base_url}/recuperacao/redefinir/{token_recuperacao}"
            
            html_content = self._get_template_recuperacao(destinatario_nome, link_recuperacao)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = destinatario_email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            
            tempo_processamento = int((time.time() - inicio_tempo) * 1000)
            
            logger.info(f"Email de recuperação enviado para {destinatario_email}")
            
            self._registrar_log_email(
                tipo_email="recuperacao_senha",
                destinatario=destinatario_email,
                assunto=assunto,
                status="enviado",
                ip_origem=ip_origem,
                user_agent=user_agent,
                tempo_processamento_ms=tempo_processamento
            )
            
            return True
            
        except Exception as e:
            tempo_processamento = int((time.time() - inicio_tempo) * 1000)
            erro_str = str(e)
            
            logger.error(f"Erro ao enviar email de recuperação: {erro_str}")
            
            self._registrar_log_email(
                tipo_email="recuperacao_senha",
                destinatario=destinatario_email,
                assunto=assunto,
                status="erro",
                erro=erro_str,
                ip_origem=ip_origem,
                user_agent=user_agent,
                tempo_processamento_ms=tempo_processamento
            )
            
            return False

    def _get_template_recuperacao(self, nome_usuario, link_recuperacao):
        """Template HTML para email de recuperação de senha"""
        template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperação de Senha - FAD</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f7f9; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; }
        .header { background: #003366; color: white; padding: 30px; text-align: center; }
        .content { padding: 30px; }
        .button { background: #006699; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; }
        .warning { background: #fff3cd; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Recuperação de Senha</h1>
            <p>FAD - Ferramenta de Análise Dinamizada</p>
        </div>
        
        <div class="content">
            <h2>Olá, """ + nome_usuario + """!</h2>
            
            <p>Você solicitou a recuperação de senha para sua conta na plataforma FAD.</p>
            
            <p>Para redefinir sua senha, clique no botão abaixo:</p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href=" """ + link_recuperacao + """ " class="button">Redefinir Minha Senha</a>
            </p>
            
            <div class="warning">
                <strong>Importante:</strong> Este link expira em 15 minutos por motivos de segurança.
            </div>
            
            <p>Se você não solicitou esta recuperação, ignore este email.</p>
        </div>
        
        <div class="footer">
            <p>FAD - Ferramenta de Análise Dinamizada</p>
            <p>Este é um email automático, não responda a esta mensagem.</p>
        </div>
    </div>
</body>
</html>
        """
        return template

    def enviar_email_confirmacao_cadastro(self, destinatario_email, destinatario_nome, 
                                        comprovante_pdf_path, dados_cadastro=None,
                                        ip_origem=None, user_agent=None):
        """Envia email de confirmação de cadastro com PDF anexo"""
        inicio_tempo = time.time()
        assunto = "FAD - Confirmação de Cadastro de Usuário"
        
        try:
            environment = os.getenv("ENVIRONMENT", "development")
            
            tamanho_anexo = None
            if comprovante_pdf_path and os.path.exists(comprovante_pdf_path):
                tamanho_anexo = os.path.getsize(comprovante_pdf_path)
            
            # Modo desenvolvimento
            if (environment == "development" or not self.smtp_password or 
                self.smtp_password in ["", "sua_senha_de_app_aqui", "Malditas131533*", "DESENVOLVIMENTO"]):
                
                print("=" * 60)
                print("MODO DESENVOLVIMENTO - EMAIL SIMULADO")
                print("=" * 60)
                print(f"Para: {destinatario_email}")
                print(f"Nome: {destinatario_nome}")
                print(f"Assunto: {assunto}")
                print(f"Anexo: {comprovante_pdf_path}")
                if tamanho_anexo:
                    print(f"Tamanho: {tamanho_anexo} bytes")
                print("=" * 60)
                
                tempo_processamento = int((time.time() - inicio_tempo) * 1000)
                self._registrar_log_email(
                    tipo_email="confirmacao_cadastro",
                    destinatario=destinatario_email,
                    assunto=assunto,
                    status="simulado_dev",
                    tamanho_anexo=tamanho_anexo,
                    ip_origem=ip_origem,
                    user_agent=user_agent,
                    tempo_processamento_ms=tempo_processamento
                )
                
                return True
            
            # Modo produção
            html_content = self._get_template_confirmacao(destinatario_nome, dados_cadastro)
            
            msg = MIMEMultipart()
            msg['Subject'] = assunto
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = destinatario_email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Adiciona anexo PDF
            if comprovante_pdf_path and os.path.exists(comprovante_pdf_path):
                with open(comprovante_pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="comprovante_cadastro_{destinatario_nome.replace(" ", "_")}.pdf"'
                )
                msg.attach(part)
            
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            
            tempo_processamento = int((time.time() - inicio_tempo) * 1000)
            
            logger.info(f"Email de confirmação enviado para {destinatario_email}")
            
            self._registrar_log_email(
                tipo_email="confirmacao_cadastro",
                destinatario=destinatario_email,
                assunto=assunto,
                status="enviado",
                tamanho_anexo=tamanho_anexo,
                ip_origem=ip_origem,
                user_agent=user_agent,
                tempo_processamento_ms=tempo_processamento
            )
            
            return True
            
        except Exception as e:
            tempo_processamento = int((time.time() - inicio_tempo) * 1000)
            erro_str = str(e)
            
            logger.error(f"Erro ao enviar email de confirmação: {erro_str}")
            
            self._registrar_log_email(
                tipo_email="confirmacao_cadastro",
                destinatario=destinatario_email,
                assunto=assunto,
                status="erro",
                erro=erro_str,
                tamanho_anexo=tamanho_anexo,
                ip_origem=ip_origem,
                user_agent=user_agent,
                tempo_processamento_ms=tempo_processamento
            )
            
            return False

    def _get_template_confirmacao(self, nome_usuario, dados_cadastro):
        """Template HTML para email de confirmação de cadastro"""
        template = """
<!DOCTYPE html>
<html lang=\"pt-br\">
<head>
    <meta charset=\"UTF-8\">\
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\
    <title>Solicitação de Cadastro de Usuário Confirmada - FAD</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f7f9; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; }
        .header { background: linear-gradient(90deg, #003366 60%, #006699 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { color: #fff; font-weight: 700; letter-spacing: 0.5px; }
        .header p { color: #e0eaf6; margin-top: 8px; }
        .content { padding: 30px; }
        .success-box { background: #e3f2fd; color: #003366; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 5px solid #006699; }
        .success-box h3 { color: #006699; margin-top: 0; }
        .footer { background: #f4f7fb; padding: 20px; text-align: center; font-size: 12px; color: #003366; border-top: 1px solid #e0eaf6; }
        ul { color: #003366; }
        strong { color: #006699; }
        @media (max-width: 700px) {
            .container { max-width: 100% !important; }
            .content { padding: 16px; }
        }
    </style>
</head>
<body>
    <div class=\"container\">
        <div class=\"header\">
            <h1>Solicitação de Cadastro de Usuário Confirmada</h1>
            <p>FAD - Ferramenta de Análise Dinamizada</p>
        </div>
        
        <div class=\"content\">
            <h2>Parabéns, """ + nome_usuario + """!</h2>
            
            <div class=\"success-box\">
                <h3>Sua solicitação de cadastro de usuário foi realizada com sucesso!</h3>
                <p>Bem-vindo à Plataforma FAD de Análise Dinamizada</p>
            </div>
            
            <p>Sua solicitação de cadastro de usuário foi processada e confirmada no sistema FAD e está em análise pela nossa equipe. Nós avisaremos assim que seu cadastro for aprovado e ativado. Por enquanto, pedimos que aguarde e teste suas credenciais na página de login.<br>Você deverá receber a mensagem <strong>\"Aguardando aprovação\"</strong>.<br>Em anexo, você encontrará o comprovante oficial do seu registro.</p>
            
            <p><strong>Próximos passos:</strong></p>
            <ul>
                <li>Guarde o comprovante em anexo para seus registros</li>
                <li>Acesse a plataforma com suas credenciais</li>
                <li>Complete seu perfil se necessário</li>
            </ul>
        </div>
        
        <div class=\"footer\">
            <p>FAD - Ferramenta de Análise Dinamizada</p>
            <p>Este é um email automático, não responda.</p>
        </div>
    </div>
</body>
</html>
        """
        return template

    def testar_configuracao(self):
        """Testa a configuração do serviço de email"""
        try:
            logger.info("Testando configuração de email...")
            
            if not self.smtp_password:
                logger.error("SMTP_PASSWORD não configurado")
                return False
                
            if self.smtp_password in ["sua_senha_de_app_aqui", "Malditas131533*", "DESENVOLVIMENTO"]:
                logger.error("SMTP_PASSWORD contém valor padrão")
                return False
            
            server = self._create_smtp_connection()
            server.quit()
            
            logger.info("Configuração de email está correta!")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração de email: {e}")
            return False


# Instância global do serviço de email
email_service = EmailService()

# Código para validação e atualização de elementos (exemplo de uso)
def validar_atualizacao_elementos(caminho_arquivo):
    """
    Valida e atualiza elementos em um arquivo de configuração ou dados.
    
    Args:
        caminho_arquivo (str): Caminho para o arquivo a ser validado/atualizado.
        
    Returns:
        bool: True se a validação e atualização forem bem-sucedidas, False caso contrário.
    """
    try:
        if not os.path.exists(caminho_arquivo):
            logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
            return False
        
        # Lógica de validação e atualização
        with open(caminho_arquivo, 'r') as file:
            conteudo = file.readlines()
        
        # Exemplo: Atualiza uma linha específica
        for i, linha in enumerate(conteudo):
            if "valor_antigo" in linha:
                conteudo[i] = linha.replace("valor_antigo", "novo_valor")
                logger.info("Atualizado valor_antigo para novo_valor")
        
        with open(caminho_arquivo, 'w') as file:
            file.writelines(conteudo)
        
        logger.info("Validação e atualização concluídas com sucesso")
        return True
    
    except Exception as e:
        logger.error(f"Erro na validação/atualização de elementos: {e}")
        return False

# Exemplo de chamada da função de validação/atualização
validar_atualizacao_elementos("_LIXO_FAD_20250612/validar_atualizacao_elementos.py")
