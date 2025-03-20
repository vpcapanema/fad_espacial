import os

# Caminhos dos arquivos onde a conexão precisa ser corrigida
arquivos_para_corrigir = [
    "app/main.py",
    "app/database/session.py",
    ".env",
    "test_db.py"
]

# Conexão antiga e nova
conexao_antiga = "fad-geospatial.c7cu4eq2gc56.us-east-2.rds.amazonaws.com"
conexao_nova = "fad-db.c7cu4eq2gc56.us-east-2.rds.amazonaws.com"

# Usuário e senha
usuario_antigo = "postgres"
usuario_novo = "vinicius"
senha_nova = "Malditas131533*"

# Função para corrigir os arquivos
def corrigir_string_conexao():
    for arquivo in arquivos_para_corrigir:
        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()

            # Substituir a string de conexão antiga pela nova
            novo_conteudo = conteudo.replace(conexao_antiga, conexao_nova).replace(usuario_antigo, usuario_novo)

            # Reescrever o arquivo corrigido
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)

            print(f"✅ Arquivo corrigido: {arquivo}")
        else:
            print(f"⚠️ Arquivo não encontrado: {arquivo}")

# Criar ou atualizar o arquivo test_db.py com a string correta
test_db_content = f"""
from sqlalchemy import create_engine

# String de conexão corrigida
DATABASE_URL = "postgresql://{usuario_novo}:{senha_nova}@{conexao_nova}:5432/postgres?sslmode=require"

# Criar engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("✅ Conexão bem-sucedida ao banco fad-db!")
except Exception as e:
    print(f"❌ Erro ao conectar: {{e}}")
"""

# Criar ou sobrescrever test_db.py
test_db_path = "test_db.py"
with open(test_db_path, "w", encoding="utf-8") as f:
    f.write(test_db_content)

print("✅ Arquivo test_db.py atualizado com sucesso!")

# Executar a correção nos outros arquivos
corrigir_string_conexao()
print("🎯 Conexão migrada para fad-db com sucesso!")
