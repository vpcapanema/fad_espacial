import re

# 📌 Caminhos exatos baseados na estrutura do projeto
upload_js_path = "/workspaces/fad_espacial/app/static/upload.js"
index_html_path = "/workspaces/fad_espacial/app/templates/index.html"
styles_css_path = "/workspaces/fad_espacial/app/static/styles.css"

# ✅ Corrigir `upload.js`
with open(upload_js_path, "r", encoding="utf-8") as file:
    upload_js_content = file.read()

# 🔹 Corrigir erro na exibição do nome do arquivo selecionado
upload_js_content = re.sub(
    r'fileInput.addEventListener\("change", function\s*\(.*?\)\s*\{[^}]+\}',
    '''
    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            fileNameField.value = fileInput.files[0].name;
        } else {
            fileNameField.value = "Selecionar arquivo";
        }
    });
    ''',
    upload_js_content,
    flags=re.DOTALL
)

# 🔹 Corrigir erro de sintaxe na linha 44
upload_js_content = re.sub(
    r'uploadProgress\.value = \(".*?"\);',  
    'uploadProgress.value = 100;',  
    upload_js_content
)

# 🔹 Ajustar a barra de progresso para acompanhar o upload real
upload_js_content = re.sub(
    r'let progress = 0;\s+const interval = setInterval\(.*?\);',
    '''
    uploadProgress.value = 0;
    fetch("/validacao/upload", {
        method: "POST",
        body: formData
    }).then(response => {
        if (!response.ok) throw new Error("Erro no upload");
        const reader = response.body.getReader();
        let receivedLength = 0;
        const contentLength = +response.headers.get("Content-Length");

        function updateProgress({ done, value }) {
            if (done) {
                uploadProgress.value = 100;
                return response.json();
            }
            receivedLength += value.length;
            uploadProgress.value = Math.min((receivedLength / contentLength) * 100, 100);
            return reader.read().then(updateProgress);
        }

        return reader.read().then(updateProgress);
    })
    .then(data => {
        if (data.success) {
            fileNameField.value = "Selecionar arquivo";
            fileInput.value = "";
            progressContainer.style.display = "none";
            resultMessage.classList.remove("hidden");
        } else {
            alert("Erro ao enviar o arquivo.");
        }
    }).catch(error => alert(error));
    ''',
    upload_js_content,
    flags=re.DOTALL
)

with open(upload_js_path, "w", encoding="utf-8") as file:
    file.write(upload_js_content)

# ✅ Corrigir `index.html`
with open(index_html_path, "r", encoding="utf-8") as file:
    index_html_content = file.read()

# 🔹 Corrigir caminhos dos arquivos CSS e JS
index_html_content = re.sub(r'href="styles.css"', 'href="/static/styles.css"', index_html_content)
index_html_content = re.sub(r'src="scripts.js"', 'src="/static/upload.js"', index_html_content)

with open(index_html_path, "w", encoding="utf-8") as file:
    file.write(index_html_content)

# ✅ Corrigir `styles.css`
with open(styles_css_path, "r", encoding="utf-8") as file:
    styles_css_content = file.read()

# 🔹 Melhorar o design da caixa de mensagem e dos botões
styles_css_content = re.sub(
    r'#resultMessage {[^}]+}',
    '''#resultMessage {
        background: #e7f3e7;
        padding: 20px;
        margin-top: 15px;
        border-radius: 10px;
        text-align: center;
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
    }''',
    styles_css_content,
    flags=re.DOTALL
)

# 🔹 Melhorar espaçamento e alinhamento dos botões "Sim" e "Não"
styles_css_content = re.sub(
    r'\.button-group {[^}]+}',
    '''.button-group {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 10px;
    }''',
    styles_css_content,
    flags=re.DOTALL
)

# 🔹 Melhorar aparência dos botões
styles_css_content += '''
#validateYes, #validateNo {
    padding: 12px 20px;
    font-size: 16px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: 0.3s;
}

#validateYes {
    background-color: #28a745;
    color: white;
}

#validateNo {
    background-color: #dc3545;
    color: white;
}

#validateYes:hover {
    background-color: #218838;
}

#validateNo:hover {
    background-color: #c82333;
}
'''

with open(styles_css_path, "w", encoding="utf-8") as file:
    file.write(styles_css_content)

print("✅ Todas as correções foram aplicadas com sucesso!")
