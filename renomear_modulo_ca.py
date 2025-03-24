import os

print("🚀 Iniciando correções no projeto FAD...")

# Caminhos base
base_path = "/workspaces/fad_espacial/app"

# Arquivos a corrigir
arquivos = ['ca_processador.py', 'ca_endpoint.py', 'validacao_geometria.py']

# Aplicar correções
for arquivo in arquivos:
    caminho = os.path.join(base_path, "modules/conformidade_ambiental" if "ca_" in arquivo else "api/endpoints", arquivo)
    if not os.path.exists(caminho):
        caminho = os.path.join(base_path, "api/endpoints", arquivo) if "validacao" in arquivo else caminho
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()

        if arquivo == "validacao_geometria.py":
            if "from geoalchemy2 import WKTElement" not in conteudo:
                conteudo = conteudo.replace("from fastapi.responses import JSONResponse", "from fastapi.responses import JSONResponse\nfrom geoalchemy2 import WKTElement\nfrom app.models.trechos_validados import TrechoValidado")
            if "db.refresh(validacao)" in conteudo and "trechos_validados" not in conteudo:
                conteudo = conteudo.replace("db.refresh(validacao)", "db.refresh(validacao)" + correcoes[arquivo]["codigo_insercao_geometria"])

        if arquivo == "ca_endpoint.py":
            for linha in correcoes[arquivo]["imports"]:
                if linha not in conteudo:
                    conteudo = linha + "\n" + conteudo

        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"✅ Corrigido: {arquivo}")

print("✅ Todas as correções foram aplicadas com sucesso!")
