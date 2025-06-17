#!/usr/bin/env python3
"""
Script para unificar cabeçalhos usando o fad_header.html EXISTENTE
NÃO altera a estrutura do fad_header.html, apenas aplica ele nas páginas
"""

import os
import re
from pathlib import Path

def tem_cabecalho_proprio(content):
    """Verifica se a página tem cabeçalho próprio que deve ser substituído"""
    patterns = [
        r'<header[^>]*>.*?</header>',
        r'class="fad-header"',
        r'\.fad-header\s*{',
        r'background.*#004080',
        r'FAD.*Ferramenta.*Análise.*Dinamizada'
    ]
    
    for pattern in patterns:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            return True
    return False

def ja_tem_fad_header(content):
    """Verifica se já inclui o fad_header.html"""
    return 'fad_header.html' in content

def adicionar_fad_header(file_path):
    """Adiciona o include do fad_header.html logo após a tag <body>"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Se já tem fad_header, não faz nada
        if ja_tem_fad_header(content):
            return f"✅ {file_path.name} - Já usa fad_header.html"
        
        # Se é home.html, pula (exceção)
        if 'home.html' in file_path.name:
            return f"⏭️ {file_path.name} - Pulado (home.html mantém cabeçalho próprio)"
        
        # Adiciona include após <body>
        if '<body>' in content:
            content = content.replace('<body>', '<body>\n  {% include \'componentes/fad_header.html\' %}')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ {file_path.name} - fad_header.html adicionado"
        elif '<body' in content:
            # Para casos como <body class="...">
            content = re.sub(r'(<body[^>]*>)', r'\1\n  {% include \'componentes/fad_header.html\' %}', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ {file_path.name} - fad_header.html adicionado"
        else:
            return f"⚠️ {file_path.name} - Não encontrou tag <body>"
            
    except Exception as e:
        return f"❌ {file_path.name} - Erro: {e}"

def main():
    templates_dir = Path("app/templates")
    resultados = []
    
    print("🔧 UNIFICANDO CABEÇALHOS - USANDO fad_header.html EXISTENTE")
    print("="*70)
    
    # Buscar todos os arquivos HTML (exceto componentes e alguns específicos)
    for html_file in templates_dir.rglob("*.html"):
        # Pular arquivos que não devem ser alterados
        if any(skip in str(html_file) for skip in [
            'componentes/', 'template_', 'backup', 'fad_header.html',
            'au_', 'ca_laudo', 'ca_processamento', 'botao_logout'
        ]):
            continue
            
        resultado = adicionar_fad_header(html_file)
        resultados.append(resultado)
        print(resultado)
    
    print("="*70)
    print(f"Total de arquivos processados: {len(resultados)}")
    
    # Estatísticas
    adicionados = sum(1 for r in resultados if "adicionado" in r)
    ja_tinham = sum(1 for r in resultados if "Já usa" in r)
    pulados = sum(1 for r in resultados if "Pulado" in r)
    
    print(f"\n📊 RESUMO:")
    print(f"- fad_header.html ADICIONADO: {adicionados}")
    print(f"- Já usavam fad_header.html: {ja_tinham}")
    print(f"- Pulados (exceções): {pulados}")

if __name__ == "__main__":
    main()
