import os

def gerar_arvore(diretorio, nivel_maximo, nivel_atual=0, prefixo=""):
    if nivel_atual >= nivel_maximo:
        return ""
    
    arvore = ""
    itens = os.listdir(diretorio)
    itens = [item for item in itens if not item.startswith('.')]  # Ignorar arquivos ocultos
    
    for i, item in enumerate(itens):
        caminho_completo = os.path.join(diretorio, item)
        if os.path.isdir(caminho_completo):
            arvore += f"{prefixo}+-- {item}/\n"
            arvore += gerar_arvore(caminho_completo, nivel_maximo, nivel_atual + 1, prefixo + "|   ")
        else:
            arvore += f"{prefixo}+-- {item}\n"
    
    return arvore

def exportar_arvore_para_txt(diretorio, nivel_maximo, arquivo_saida):
    arvore = gerar_arvore(diretorio, nivel_maximo)
    with open(arquivo_saida, 'w') as f:
        f.write(arvore)
    print(f"Árvore de diretórios exportada para {arquivo_saida}")

# Defina o diretório raiz do seu projeto
diretorio_raiz = "/workspaces/fad_espacial"  # Substitua pelo caminho do seu projeto no Codespace
nivel_maximo = 5
arquivo_saida = "arvore_diretorios.txt"

exportar_arvore_para_txt(diretorio_raiz, nivel_maximo, arquivo_saida)