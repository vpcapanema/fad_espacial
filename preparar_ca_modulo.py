import os
import zipfile

# 1. Renomear arquivos antigos
renomeacoes = {
    "app/api/endpoints/conformidade_ambiental.py": "app/api/endpoints/ca_endpoint.py",
    "app/modules/conformidade_ambiental/processador.py": "app/modules/conformidade_ambiental/ca_processador.py",
    "app/modules/conformidade_ambiental/relatorio.py": "app/modules/conformidade_ambiental/ca_laudo.py",
    "app/modules/conformidade_ambiental/relatorio_processamento.py": "app/modules/conformidade_ambiental/ca_processamento.py",
    "app/modules/conformidade_ambiental/gerador_shapefile.py": "app/modules/conformidade_ambiental/ca_shapefile.py",
    "app/modules/conformidade_ambiental/mapa.py": "app/modules/conformidade_ambiental/ca_mapa.py",
    "app/templates/conformidade_ambiental.html": "app/templates/ca_interface.html",
    "app/templates/relatorio_conformidade.html": "app/templates/ca_laudo_template.html"
}

for original, novo in renomeacoes.items():
    if os.path.exists(original) and not os.path.exists(novo):
        os.rename(original, novo)
        print(f"✔️ Renomeado: {original} → {novo}")

# 2. Criar arquivos faltantes
arquivos_para_criar = {
    "app/templates/ca_processamento_template.html": """<!DOCTYPE html>
<html lang="pt-br">
<head><meta charset="UTF-8"><title>Relatório Técnico de Processamento</title></head>
<body><h1>Relatório Técnico - Módulo de Conformidade Ambiental</h1></body>
</html>"""
}

for caminho, conteudo in arquivos_para_criar.items():
    if not os.path.exists(caminho):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"🆕 Criado: {caminho}")

# 3. Criar zip com todos os arquivos do módulo `ca_`
caminhos_ca = []
for root, dirs, files in os.walk("app"):
    for file in files:
        if file.startswith("ca_") or "conformidade_ambiental" in root:
            caminhos_ca.append(os.path.join(root, file))

zip_path = "ca_modulo.zip"
with zipfile.ZipFile(zip_path, "w") as zipf:
    for caminho in caminhos_ca:
        zipf.write(caminho)
        print(f"📦 Adicionado ao ZIP: {caminho}")

print(f"\n✅ Arquivo gerado: {zip_path}")
print("→ Pronto para enviar para análise.")
