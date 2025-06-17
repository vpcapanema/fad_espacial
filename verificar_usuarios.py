#!/usr/bin/env python3
"""
Script para verificar e atualizar usuários no banco
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from app.database.session import SessionLocal
from app.models.cd_usuario_sistema import UsuarioSistema

def main():
    print("🔍 Verificando usuários no banco...")
    
    db = SessionLocal()
    
    try:
        # Verificar usuários com CPF específico
        cpf = '01499296177'
        usuarios = db.query(UsuarioSistema).filter(UsuarioSistema.cpf == cpf).all()
        
        print(f"\n📋 Usuários com CPF {cpf}:")
        for u in usuarios:
            print(f"  ID: {u.id} | Nome: {u.nome} | Tipo: {u.tipo} | Status: {u.status} | Ativo: {u.ativo}")
        
        # Verificar todos os masters
        masters = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == 'master').all()
        print(f"\n👑 Usuários master no sistema ({len(masters)}):")
        for m in masters:
            print(f"  ID: {m.id} | Nome: {m.nome} | CPF: {m.cpf} | Status: {m.status}")
        
        # Se não há master, criar um baseado no usuário ID 5
        if len(masters) == 0:
            print(f"\n🚀 Não há usuários master. Atualizando usuário ID 5...")
            usuario_5 = db.query(UsuarioSistema).filter(UsuarioSistema.id == 5).first()
            if usuario_5:
                usuario_5.tipo = 'master'
                usuario_5.status = 'aprovado'
                usuario_5.ativo = True
                db.commit()
                print(f"✅ Usuário ID 5 ({usuario_5.nome}) agora é MASTER")
            else:
                print("❌ Usuário ID 5 não encontrado")
        else:
            print("✅ Já existe pelo menos um usuário master")
        
        # Verificar novamente após atualização
        masters = db.query(UsuarioSistema).filter(UsuarioSistema.tipo == 'master').all()
        print(f"\n🎯 RESULTADO FINAL - Masters no sistema:")
        for m in masters:
            print(f"  ID: {m.id} | Nome: {m.nome} | CPF: {m.cpf} | Status: {m.status} | Ativo: {m.ativo}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
