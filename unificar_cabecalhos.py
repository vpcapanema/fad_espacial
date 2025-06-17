#!/usr/bin/env python3
"""
Script para unificar cabeçalhos usando fad_header.html
"""

import os
import re
from pathlib import Path

def atualizar_template(file_path):
    """Atualiza um template para usar fad_header.html"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        arquivo = Path(file_path).name
        
        # Pular home.html e arquivos que já usam fad_header.html
        if arquivo == 'home.html' or 'fad_header.html' in content:
            return False, "Arquivo ignorado (home.html ou já usa fad_header.html)"
        
        # Pular componentes e templates internos
        if any(skip in arquivo.lower() for skip in ['fad_header.html', 'template_cabecalho', 'componentes/']):
            return False, "Componente interno - ignorado"
        
        modificado = False
        content_original = content
        
        # Remover headers próprios existentes
        patterns_to_remove = [
            r'<header[^>]*>.*?</header>',
            r'<div[^>]*class="?hero"?[^>]*>.*?</div>',
            r'<div[^>]*class="?header"?[^>]*>.*?</div>',
            r'<div[^>]*fad-header[^>]*>.*?</div>'
        ]
        
        for pattern in patterns_to_remove:
            new_content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
            if new_content != content:
                content = new_content
                modificado = True
        
        # Adicionar include do fad_header.html após <body>
        if '<body>' in content and '{% include \'componentes/fad_header.html\' %}' not in content:
            content = content.replace('<body>', '<body>\n  {% include \'componentes/fad_header.html\' %}')
            modificado = True
        elif '<body' in content and '{% include \'componentes/fad_header.html\' %}' not in content:
            # Buscar tag body com atributos
            body_match = re.search(r'<body[^>]*>', content)
            if body_match:
                body_tag = body_match.group(0)
                content = content.replace(body_tag, body_tag + '\n  {% include \'componentes/fad_header.html\' %}')
                modificado = True
        
        if modificado:
            # Fazer backup
            backup_path = file_path.replace('.html', '_backup_header.html')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content_original)
            
            # Salvar arquivo modificado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "Atualizado com sucesso"
        else:
            return False, "Nenhuma modificação necessária"
            
    except Exception as e:
        return False, f"Erro: {e}"

def main():
    templates_dir = Path("app/templates")
    resultados = []
    
    print("🔄 UNIFICANDO CABEÇALHOS PARA fad_header.html")
    print("="*60)
    
    # Buscar todos os arquivos HTML (exceto em subdiretorios de componentes)
    for html_file in templates_dir.rglob("*.html"):
        # Pular componentes
        if 'componentes' in str(html_file):
            continue
            
        sucesso, mensagem = atualizar_template(html_file)
        
        arquivo = html_file.name
        status = "✅ ATUALIZADO" if sucesso else "⏭️ IGNORADO"
        
        print(f"{status:<12} {arquivo:<35} {mensagem}")
        
        resultados.append({
            'arquivo': arquivo,
            'sucesso': sucesso,
            'mensagem': mensagem
        })
    
    print("="*60)
    
    # Estatísticas
    atualizados = sum(1 for r in resultados if r['sucesso'])
    total = len(resultados)
    
    print(f"📊 RESULTADO:")
    print(f"   - Arquivos processados: {total}")
    print(f"   - Arquivos atualizados: {atualizados}")
    print(f"   - Arquivos ignorados: {total - atualizados}")
    
    if atualizados > 0:
        print(f"\n💾 Backups criados com sufixo '_backup_header.html'")
        print(f"🎯 Todos os arquivos agora usam fad_header.html!")

if __name__ == "__main__":
    main()
