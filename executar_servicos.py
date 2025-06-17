#!/usr/bin/env python3
"""
Script para executar serviços de formulário e email para usuários existentes
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
import tempfile

def main():
    print("🔧 Executando serviços de formulário e email...")
    
    # Criar serviços
    formulario_service = FormularioService()
    email_service = EmailService()
    
    # IDs dos usuários para processar
    user_ids = [2, 4, 5]
    
    for user_id in user_ids:
        print(f"\n📝 Processando usuário ID {user_id}...")
        
        # Nova sessão para cada usuário
        db = SessionLocal()
        
        try:
            # Buscar usuário
            usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == user_id).first()
            if not usuario:
                print(f"❌ Usuário ID {user_id} não encontrado")
                continue
            
            print(f"   👤 {usuario.nome} ({usuario.tipo})")
            print(f"   📧 {usuario.email_institucional or usuario.email}")
            
            # 1. Gerar formulário HTML
            print(f"   📄 Gerando formulário HTML...")
            formulario_html = formulario_service.gerar_formulario_html(db, user_id)
            print(f"   ✅ HTML: {formulario_html}")
            
            # 2. Gerar PDF do formulário
            print(f"   📑 Gerando PDF...")
            formulario_pdf = formulario_html.replace('.html', '.pdf')
            
            # Simular geração de PDF (usar pdfkit se disponível)
            try:
                import pdfkit
                options = {
                    'page-size': 'A4',
                    'orientation': 'Portrait',
                    'margin-top': '10mm',
                    'margin-right': '10mm',
                    'margin-bottom': '10mm',
                    'margin-left': '10mm',
                    'dpi': 300,
                    'encoding': 'UTF-8'
                }
                pdfkit.from_file(formulario_html, formulario_pdf, options=options)
                print(f"   ✅ PDF: {formulario_pdf}")
            except Exception as e:
                print(f"   ⚠️ PDF não gerado: {e}")
                formulario_pdf = None
            
            # 3. Enviar email de confirmação
            print(f"   📧 Enviando email...")
            email_destinatario = usuario.email_institucional or usuario.email
            
            email_enviado = email_service.enviar_email_confirmacao_cadastro(
                destinatario_email=email_destinatario,
                destinatario_nome=usuario.nome,
                comprovante_pdf_path=formulario_pdf,
                dados_cadastro={
                    'nome': usuario.nome,
                    'cpf': usuario.cpf,
                    'tipo': usuario.tipo,
                    'email_institucional': usuario.email_institucional,
                    'instituicao': usuario.instituicao,
                    'status': 'Processado via script'
                },
                ip_origem='127.0.0.1',
                user_agent='Script de Processamento'
            )
            
            if email_enviado:
                print(f"   ✅ Email enviado com sucesso!")
            else:
                print(f"   ⚠️ Email simulado (modo desenvolvimento)")
            
            db.commit()
            print(f"✅ ID {user_id}: Processamento completo!")
            
        except Exception as e:
            print(f"❌ Erro ao processar ID {user_id}: {str(e)}")
            db.rollback()
            import traceback
            print(f"   Detalhes: {traceback.format_exc()}")
            
        finally:
            db.close()
    
    print("\n🏁 Todos os serviços executados!")

if __name__ == "__main__":
    main()
