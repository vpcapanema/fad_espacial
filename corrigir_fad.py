import os

# Caminhos dos arquivos
index_html_path = "/workspaces/fad_espacial/app/templates/index.html"
upload_js_path = "/workspaces/fad_espacial/app/static/upload.js"
styles_css_path = "/workspaces/fad_espacial/app/static/styles.css"
main_py_path = "/workspaces/fad_espacial/app/main.py"

# Novo conteúdo corrigido para index.html
index_html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ferramenta de Análise Dinamizada (FAD)</title>
    
    <!-- Bootstrap -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    
    <!-- Arquivo de Estilos -->
    <link rel="stylesheet" href="{{ url_for('static', path='styles.css') }}">
</head>
<body>
    <div class="container">
        <header class="py-4">
            <h1 class="fw-bold">Ferramenta de Análise Dinamizada (FAD)</h1>
            <h2 class="h5">Sistema de Importação de Arquivos</h2>
        </header>

        <!-- Seção de Upload -->
        <div class="upload-container">
            <h2>Importação de Arquivo</h2>
            <p>Envie um arquivo ZIP para ser armazenado no banco.</p>
            
            <div class="upload-row">
                <label for="arquivo" class="custom-file-label">Escolher arquivo</label>
                <input type="file" id="arquivo" class="custom-file-input" accept=".zip">
                <div class="file-name-box" id="file-name">Nenhum arquivo selecionado</div>
                <button class="btn btn-primary" onclick="enviarArquivo()">Enviar</button>
            </div>

            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%;"></div>
            </div>

            <div id="mensagem" class="alert" role="alert"></div>
        </div>
    </div>

    <!-- Importação do arquivo de script externo -->
    <script src="{{ url_for('static', path='upload.js') }}"></script>
</body>
</html>
"""

# Novo conteúdo corrigido para upload.js
upload_js_content = """document.getElementById("arquivo").addEventListener("change", function() {
    let fileName = this.files[0] ? this.files[0].name : "Nenhum arquivo selecionado";
    document.getElementById("file-name").innerText = fileName;
});

function enviarArquivo() {
    let input = document.getElementById("arquivo").files[0];
    if (!input) {
        alert("Selecione um arquivo para enviar.");
        return;
    }

    // Verifica se o arquivo é um ZIP
    if (!input.name.endsWith(".zip")) {
        alert("O arquivo deve ser um ZIP.");
        return;
    }

    let formData = new FormData();
    formData.append("arquivo", input);

    let progressBar = document.querySelector(".progress");
    let progressBarInner = document.querySelector(".progress-bar");
    let mensagem = document.getElementById("mensagem");

    progressBar.style.display = "block";
    progressBarInner.style.width = "0%";
    mensagem.style.display = "none";

    // URL do backend corrigida
    const backendUrl = "/validacao/upload/";

    fetch(backendUrl, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        progressBarInner.style.width = "100%";
        setTimeout(() => {
            progressBar.style.display = "none";
            mensagem.style.display = "block";
            if (data.sucesso) {
                mensagem.className = "alert alert-success";
                mensagem.innerHTML = "Arquivo importado com sucesso!";
            } else {
                mensagem.className = "alert alert-danger";
                mensagem.innerHTML = "Falha na importação. Tente novamente!";
            }
        }, 1000);
    })
    .catch(error => {
        console.error("Erro ao enviar arquivo:", error);
        progressBar.style.display = "none";
        mensagem.style.display = "block";
        mensagem.className = "alert alert-danger";
        mensagem.innerHTML = "Erro ao enviar arquivo: " + error.message;
    });
}
"""

# Novo conteúdo corrigido para styles.css
styles_css_content = """body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    text-align: center;
    padding: 20px;
}

.upload-container {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    width: 50%;
    margin: auto;
    text-align: center;
}

.progress {
    display: none;
    height: 20px;
    margin-top: 10px;
}

.alert {
    display: none;
    margin-top: 15px;
}
"""

# Atualização do main.py para corrigir a rota de arquivos estáticos
main_py_content = """from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Configuração correta para arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configuração do Jinja2 para templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
"""

# Função para escrever os arquivos
def corrigir_arquivos():
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(index_html_content)
    with open(upload_js_path, "w", encoding="utf-8") as f:
        f.write(upload_js_content)
    with open(styles_css_path, "w", encoding="utf-8") as f:
        f.write(styles_css_content)
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(main_py_content)

    print("✅ Todos os arquivos foram corrigidos com sucesso!")

# Executa a correção
corrigir_arquivos()
