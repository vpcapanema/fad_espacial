import zipfile
import os

# Arquivos essenciais da FAD inteira
arquivos_fad = [
    "app/main.py",
    "app/database/session.py",

    # Endpoints
    "app/api/endpoints/upload.py",
    "app/api/endpoints/validacao_geometria.py",
    "app/api/endpoints/ca_endpoint.py",

    # Modelos
    "app/models/arquivos.py",
    "app/models/validacao.py",
    "app/models/trechos_validados.py",

    # Módulo de Conformidade Ambiental
    "app/modules/conformidade_ambiental/ca_processador.py",
    "app/modules/conformidade_ambiental/ca_laudo.py",
    "app/modules/conformidade_ambiental/ca_laudo_sintetico.py",
    "app/modules/conformidade_ambiental/ca_shapefile.py",
    "app/modules/conformidade_ambiental/ca_processamento.py",
    "app/modules/conformidade_ambiental/ca_mapa.py",

    # Templates
    "app/templates/index.html",
    "app/templates/ca_interface.html",
    "app/templates/ca_laudo_template.html",
    "app/templates/ca_laudo_sintetico_template.html",
    "app/templates/ca_processamento_template.html",

    # Frontend
    "static/upload.js",
    "static/styles.css"
]

zip_path = "fad_codigo_completo.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file in arquivos_fad:
        if os.path.exists(file):
            zipf.write(file, arcname=os.path.basename(file))

print(f"✅ Arquivo criado: {zip_path}")
