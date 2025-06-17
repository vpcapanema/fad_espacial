#!/usr/bin/env python3
"""
Script para unificar cabeçalhos nos templates HTML
Aplica o fad_header.html em todas as páginas, exceto home.html
"""

import os
import re
from pathlib import Path

def processar_template(file_path):
    """Processa um template para usar o fad_header.html"""
    
    arquivo_nome = Path(file_path).name
    
    # Exceções - não processar estes arquivos
    excecoes = [
        'home.html', 
        'fad_header.html', 
        'template_cabecalho_fad.html',
        'botao_logout.html'
    ]
    
    if arquivo_nome in excecoes:
        print(f"⏭️  PULANDO: {arquivo_nome} (exceção)")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já usa fad_header.html
        if 'fad_header.html' in content:
            print(f"✅ JÁ USA FAD_HEADER: {arquivo_nome}")
            return False
        
        # Verificar se tem <body> tag
        if '<body>' not in content and '<body ' not in content:
            print(f"⚠️  SEM BODY TAG: {arquivo_nome}")
            return False
        
        # Padrão para inserir o include logo após <body>
        include_fad = '{% include \'componentes/fad_header.html\' %}'
        
        # Remover cabeçalhos existentes (se houver)
        # Remove headers próprios
        content = re.sub(r'<header[^>]*>.*?</header>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Inserir o include após <body>
        if '<body>' in content:
            content = content.replace('<body>', f'<body>\n  {include_fad}\n')
        elif '<body ' in content:
            # Para body com atributos
            body_match = re.search(r'<body[^>]*>', content)
            if body_match:
                body_tag = body_match.group(0)
                content = content.replace(body_tag, f'{body_tag}\n  {include_fad}\n')
        
        # Salvar arquivo atualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"🔄 ATUALIZADO: {arquivo_nome}")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {arquivo_nome} - {e}")
        return False

def main():
    templates_dir = Path("app/templates")
    
    print("🚀 INICIANDO UNIFICAÇÃO DE CABEÇALHOS")
    print("="*60)
    
    arquivos_processados = 0
    arquivos_atualizados = 0
    
    # Processar todos os arquivos HTML
    for html_file in templates_dir.rglob("*.html"):
        arquivos_processados += 1
        
        if processar_template(html_file):
            arquivos_atualizados += 1
    
    print("="*60)
    print(f"📊 RESUMO:")
    print(f"   Arquivos processados: {arquivos_processados}")
    print(f"   Arquivos atualizados: {arquivos_atualizados}")
    print(f"   Arquivos já padronizados: {arquivos_processados - arquivos_atualizados}")
    print("✅ UNIFICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()
