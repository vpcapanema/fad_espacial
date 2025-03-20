document.getElementById("arquivo").addEventListener("change", function() {
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
    const backendUrl = "https://urban-xylophone-4j6qpx6vw9wpcjwpv-8000.app.github.dev/validacao/upload/";


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
