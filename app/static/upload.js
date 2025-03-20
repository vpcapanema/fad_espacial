document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("fileInput");
    const fileNameField = document.getElementById("fileName");
    const uploadButton = document.getElementById("uploadButton");
    const progressContainer = document.getElementById("progressContainer");
    const uploadProgress = document.getElementById("uploadProgress");
    const resultMessage = document.getElementById("resultMessage");
    const errorMessage = document.getElementById("errorMessage");
    const validateYes = document.getElementById("validateYes");
    const validateNo = document.getElementById("validateNo");
    const errorOkButton = document.getElementById("errorOkButton");

    // 🔥 API base fixa no Codespaces
    const API_BASE_URL = "https://urban-xylophone-4j6qpx6vw9wpcjwpv-8000.app.github.dev";

    // Esconde mensagens ao carregar a página
    resultMessage.style.display = "none";
    errorMessage.style.display = "none";

    fileInput.addEventListener("change", function () {
        fileNameField.value = fileInput.files.length ? fileInput.files[0].name : "Selecionar arquivo";
    });

    uploadButton.addEventListener("click", function () {
        if (!fileInput.files.length) {
            alert("Por favor, selecione um arquivo.");
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("arquivo", file);

        progressContainer.style.display = "block";
        uploadProgress.value = 0;

        fetch(`${API_BASE_URL}/upload/`, {  // 🔥 Corrigida a URL de upload com "/" no final
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progressContainer.style.display = "none"; // Esconder barra de progresso

            if (data.sucesso) {
                resultMessage.style.display = "flex"; // 🔥 Só exibe se a importação for válida
                errorMessage.style.display = "none";
            } else {
                errorMessage.style.display = "block";
                resultMessage.style.display = "none";
            }
        })
        .catch(() => {
            progressContainer.style.display = "none";
            errorMessage.style.display = "block";
            resultMessage.style.display = "none";
        });

        let progress = 0;
        const interval = setInterval(() => {
            if (progress >= 100) {
                clearInterval(interval);
            } else {
                progress += 10;
                uploadProgress.value = progress;
            }
        }, 300);
    });

    errorOkButton.addEventListener("click", function () {
        fetch(`${API_BASE_URL}/delete-uploaded-file`, { method: "DELETE" })  // 🔥 Corrigida a URL para deletar arquivo
        .then(() => {
            window.location.reload();
        });
    });

    validateYes.addEventListener("click", function () {
        window.location.href = `${API_BASE_URL}/validar-geometria`;  // 🔥 Corrigida a URL de validação
    });

    validateNo.addEventListener("click", function () {
        fetch(`${API_BASE_URL}/delete-uploaded-file`, { method: "DELETE" })  // 🔥 Corrigida a URL de exclusão
        .then(() => {
            window.location.reload();
        });
    });
});
