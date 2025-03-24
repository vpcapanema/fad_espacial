import os

# Caminhos dos arquivos no repositório Codespaces
arquivos_para_atualizar = {
    "app/modules/conformidade_ambiental/ca_shapefile.py": {
        "substituicoes": [
            ("nome_area", "nome_area_protegida"),
            ("conformidade_ambiental_resultado.zip", "ca_arquivo_processado.zip")
        ]
    },
    "app/modules/conformidade_ambiental/ca_processamento.py": {
        "substituicoes": [
            ("processamento_conformidade_ambiental.pdf", "ca_relatorio_processamento.pdf")
        ]
    },
    "app/modules/conformidade_ambiental/ca_laudo.py": {
        "substituicoes": [
            ("laudo_conformidade_ambiental.pdf", "ca_laudo_analitico_conformidade_ambiental.pdf"),
            ("tipo_laudo == 'sintetico'", "tipo_laudo == 'sintetico'"),  # para identificar o ponto onde pode trocar nome do PDF
            ("filename=\"laudo_conformidade_ambiental.pdf\"", "filename=\"ca_laudo_sintetico_conformidade_ambiental.pdf\"")
        ]
    }
}

# Aplicar as substituições
for caminho, info in arquivos_para_atualizar.items():
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()

        for antigo, novo in info["substituicoes"]:
            conteudo = conteudo.replace(antigo, novo)

        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)

"✅ Alterações aplicadas aos arquivos diretamente no repositório Codespaces."
