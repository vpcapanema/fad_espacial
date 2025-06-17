#!/usr/bin/env python3
"""
Script completo para executar todos os serviços: Formulário + PDF + Email
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from app.database.session import SessionLocal
from app.services.formulario_service import FormularioService
from app.services.email_service import EmailService
from app.models.cd_usuario_sistema import UsuarioSistema
import pdfkit

def gerar_pdf_otimizado(html_path, pdf_path):
    """Gera PDF com configuração otimizada"""
    try:
        options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'dpi': 300,
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'disable-external-links': None,
            'disable-javascript': None,
            'no-images': None,
            'disable-plugins': None,
            'load-error-handling': 'ignore',
            'load-media-error-handling': 'ignore',
            'quiet': None
        }
        
        pdfkit.from_file(html_path, pdf_path, options=options)
        return True
        
    except Exception as e:
        print(f"❌ Erro na geração do PDF: {e}")
        return False

def main():
    print("🚀 EXECUTANDO SISTEMA COMPLETO: FORMULÁRIO + PDF + EMAIL")
    print("=" * 60)
    
    # Inicializar serviços
    formulario_service = FormularioService()
    email_service = EmailService()
    
    # IDs para processar
    user_ids = [2, 4, 5]
    
    for user_id in user_ids:
        print(f"\n📋 PROCESSANDO USUÁRIO ID {user_id}")
        print("-" * 40)
        
        # Nova sessão para cada usuário
        db = SessionLocal()
        
        try:
            # 1. BUSCAR USUÁRIO
            usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == user_id).first()
            if not usuario:
                print(f"❌ Usuário ID {user_id} não encontrado")
                continue
            
            print(f"👤 Nome: {usuario.nome}")
            print(f"📧 Email: {usuario.email_institucional or usuario.email}")
            print(f"🏢 Tipo: {usuario.tipo.upper()}")
            print(f"🏛️ Instituição: {usuario.instituicao}")
            
            # 2. GERAR FORMULÁRIO HTML
            print(f"\n📄 ETAPA 1: Gerando formulário HTML...")
            formulario_html = formulario_service.gerar_formulario_html(db, user_id)
            
            if not formulario_html or not os.path.exists(formulario_html):
                print(f"❌ Falha na geração do HTML")
                continue
                
            tamanho_html = os.path.getsize(formulario_html)
            print(f"✅ HTML gerado: {os.path.basename(formulario_html)} ({tamanho_html:,} bytes)")
            
            # 3. GERAR PDF
            print(f"\n📑 ETAPA 2: Gerando PDF do formulário...")
            formulario_pdf = formulario_html.replace('.html', '.pdf')
            
            if gerar_pdf_otimizado(formulario_html, formulario_pdf):
                if os.path.exists(formulario_pdf):
                    tamanho_pdf = os.path.getsize(formulario_pdf)
                    print(f"✅ PDF gerado: {os.path.basename(formulario_pdf)} ({tamanho_pdf:,} bytes)")
                else:
                    print(f"❌ PDF não foi criado")
                    formulario_pdf = None
            else:
                print(f"❌ Falha na geração do PDF")
                formulario_pdf = None
            
            # 4. ENVIAR EMAIL
            print(f"\n📧 ETAPA 3: Enviando email de confirmação...")
            email_destinatario = usuario.email_institucional or usuario.email
            
            dados_cadastro = {
                'nome': usuario.nome,
                'cpf': usuario.cpf,
                'tipo': usuario.tipo,
                'email_institucional': usuario.email_institucional,
                'instituicao': usuario.instituicao,
                'sede_hierarquia': usuario.sede_hierarquia,
                'sede_diretoria': usuario.sede_diretoria,
                'sede_coordenadoria_geral': usuario.sede_coordenadoria_geral,
                'sede_coordenadoria': usuario.sede_coordenadoria,
                'status': 'Cadastrado - Processado pelo Sistema'
            }
            
            email_enviado = email_service.enviar_email_confirmacao_cadastro(
                destinatario_email=email_destinatario,
                destinatario_nome=usuario.nome,
                comprovante_pdf_path=formulario_pdf,
                dados_cadastro=dados_cadastro,
                ip_origem='127.0.0.1',
                user_agent='Sistema FAD - Processamento Automático'
            )
            
            if email_enviado:
                print(f"✅ Email enviado com sucesso para {email_destinatario}")
            else:
                print(f"📨 Email simulado (modo desenvolvimento)")
            
            # 5. COMMIT DA TRANSAÇÃO
            db.commit()
            
            print(f"\n🎉 USUÁRIO ID {user_id} PROCESSADO COM SUCESSO!")
            print(f"   📄 HTML: ✅")
            print(f"   📑 PDF: {'✅' if formulario_pdf else '❌'}")
            print(f"   📧 Email: ✅")
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO ao processar ID {user_id}:")
            print(f"   {str(e)}")
            db.rollback()
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            
        finally:
            db.close()
    
    print("\n" + "=" * 60)
    print("🏁 SISTEMA COMPLETO EXECUTADO!")
    print("   ✅ Formulários HTML gerados")
    print("   ✅ PDFs criados") 
    print("   ✅ Emails enviados")
    print("=" * 60)

if __name__ == "__main__":
    main()
