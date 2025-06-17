#!/usr/bin/env python3
"""
Script simples para gerar formulários dos IDs 4 e 5
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from app.database.session import SessionLocal
from app.services.formulario_service import FormularioService

def main():
    print("🔧 Gerando formulários para IDs 4 e 5...")
    
    # Criar nova sessão para cada usuário
    service = FormularioService()
    
    for user_id in [4, 5]:
        print(f"\n📝 Processando usuário ID {user_id}...")
        
        # Nova sessão para cada usuário
        db = SessionLocal()
        
        try:
            resultado = service.gerar_formulario_html(db, user_id)
            print(f"✅ ID {user_id}: {resultado}")
            db.commit()
            
        except Exception as e:
            print(f"❌ Erro ID {user_id}: {str(e)}")
            db.rollback()
            
        finally:
            db.close()
    
    print("\n🏁 Processo finalizado!")

if __name__ == "__main__":
    main()
