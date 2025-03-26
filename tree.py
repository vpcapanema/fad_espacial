import os

def gerar_arvore_diretorios(caminho_raiz, nivel=0, max_nivel=5, arquivo_saida="arvore_diretorios.txt", arquivo=None):
    prefixo = "│   " * (nivel - 1) + ("├── " if nivel > 0 else "")
    itens = sorted(os.listdir(caminho_raiz))

    if arquivo is None:
        arquivo = open(arquivo_saida, "w", encoding="utf-8")
        fechar_arquivo = True
    else:
        fechar_arquivo = False

    for i, item in enumerate(itens):
        caminho_item = os.path.join(caminho_raiz, item)
        if os.path.isdir(caminho_item):
            arquivo.write(f"{prefixo}{item}/\n")
            if nivel < max_nivel:
                gerar_arvore_diretorios(caminho_item, nivel + 1, max_nivel, arquivo_saida, arquivo)
        else:
            arquivo.write(f"{prefixo}{item}\n")

    if fechar_arquivo:
        arquivo.close()
        print(f"✅ Arquivo '{arquivo_saida}' gerado com sucesso.")

# Use "." se quiser gerar a partir do diretório atual
gerar_arvore_diretorios(".", max_nivel=5)
