import os

# Lista de arquivos que podem conter chamadas à API
arquivos_para_corrigir = [
    "app/main.py",
    "app/database/session.py",
    ".env",
    "test_db.py",
    "index.html",
    "scripts.js",
    "config.js"  # Caso tenha um arquivo de configuração separado
]

# URL antiga e nova da API
url_antiga = "http://127.0.0.1:8000"
url_nova = "https://urban-xylophone-4j6qpx6vw9wpcjwpv-8000.app.github.dev"

# Função para corrigir os arquivos
def corrigir_url_api():
    for arquivo in arquivos_para_corrigir:
        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()

            # Substituir a URL antiga pela nova
            novo_conteudo = conteudo.replace(url_antiga, url_nova)

            # Reescrever o arquivo corrigido
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)

            print(f"✅ Arquivo atualizado: {arquivo}")
        else:
            print(f"⚠️ Arquivo não encontrado: {arquivo}")

# Executar a correção
corrigir_url_api()
print("🎯 Todos os arquivos foram atualizados para a nova URL da API!")
