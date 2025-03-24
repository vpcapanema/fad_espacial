
import os
import re

print("🚀 Iniciando atualização do fluxo FAD...")

# Caminhos dos arquivos
BASE_MODULOS = "/workspaces/fad_espacial/app/modules/conformidade_ambiental"
BASE_ENDPOINTS = "/workspaces/fad_espacial/app/api/endpoints"
BASE_TEMPLATES = "/workspaces/fad_espacial/app/templates"

# 1. Limpa validação duplicada do módulo CA
caminho_ca_proc = os.path.join(BASE_MODULOS, "ca_processador.py")
if os.path.exists(caminho_ca_proc):
    with open(caminho_ca_proc, "r", encoding="utf-8") as f:
        conteudo = f.read()
    conteudo = re.sub(r'SELECT COUNT\(\*\) FROM validacao_geometria.*?;', '', conteudo)
    with open(caminho_ca_proc, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ Limpou validações do módulo CA (ca_processador.py)")

# 2. Atualiza ca_endpoint.py para remover validação redundante, mantendo tipo de laudo
caminho_ca_ep = os.path.join(BASE_ENDPOINTS, "ca_endpoint.py")
if os.path.exists(caminho_ca_ep):
    with open(caminho_ca_ep, "r", encoding="utf-8") as f:
        conteudo = f.read()
    conteudo = re.sub(r'SELECT COUNT\(\*\) FROM validacao_geometria.*?;', '', conteudo)
    with open(caminho_ca_ep, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ Endpoint CA atualizado")

# 3. Atualiza interface de validação diretamente no index.html
caminho_index = os.path.join(BASE_TEMPLATES, "index.html")
if os.path.exists(caminho_index):
    with open(caminho_index, "r", encoding="utf-8") as f:
        html = f.read()

    # Atualiza IDs e texto do botão de validação
    html = html.replace('id="UploadReport"', 'id="downloadReport"')
    html = html.replace('Relatório de upload/p', 'Relatório de upload</p>')

    # Corrige duplicações do botão de análise dinamizada
    html = re.sub(r'<!-- NOVO: Botão para iniciar a análise dinamizada -->.*?<div id="startAnalysisContainer".*?</div>', '', html, flags=re.DOTALL)

    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ Interface index.html atualizada e corrigida")

print("🏁 Atualização concluída.")
