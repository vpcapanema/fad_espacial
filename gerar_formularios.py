#!/usr/bin/env python3
"""
Script para gerar formulários HTML dos usuários cadastrados
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    from app.database.session import SessionLocal
    from app.services.formulario_service import FormularioService
    from app.models.cd_usuario_sistema import UsuarioSistema
    
    def main():
        print("🔧 Iniciando geração de formulários...")
        
        # Criar sessão do banco
        db = SessionLocal()
        
        # Criar instância do serviço
        service = FormularioService()
        
        # IDs dos usuários para processar
        user_ids = [2, 4, 5]
        
        for user_id in user_ids:
            print(f"\n📝 Processando usuário ID {user_id}...")
            
            try:
                # Verificar se usuário existe
                usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == user_id).first()
                if not usuario:
                    print(f"❌ Usuário ID {user_id} não encontrado no banco")
                    continue
                
                print(f"   👤 {usuario.nome} ({usuario.tipo})")
                
                # Gerar formulário
                resultado = service.gerar_formulario_html(db, user_id)
                print(f"✅ ID {user_id}: {resultado}")
                
            except Exception as e:
                print(f"❌ Erro ao processar ID {user_id}: {str(e)}")
                import traceback
                print(f"   Detalhes: {traceback.format_exc()}")
        
        db.close()
        print("\n🏁 Processo finalizado!")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se o ambiente virtual está ativo e as dependências instaladas")
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    print(f"Detalhes: {traceback.format_exc()}")
