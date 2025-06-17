#!/usr/bin/env python3
"""
🔄 Script para atualizar páginas para usar o cabeçalho padronizado
"""

import os
import re
from pathlib import Path

def backup_file(file_path):
    """Cria backup do arquivo antes de modificar"""
    backup_path = str(file_path) + '.backup'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")

def update_template_for_fad_header(file_path):
    """Atualiza um template para usar o fad_header.html"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Verificar se já usa fad_header.html
    if "{% include 'componentes/fad_header.html' %}" in content:
        print(f"⏭️ {file_path.name} já usa fad_header.html")
        return False
    
    # Padrões de cabeçalho para substituir
    header_patterns = [
        # Cabeçalho HTML direto
        r'<header[^>]*class=["\']fad-header["\'][^>]*>.*?</header>',
        r'<header[^>]*>.*?FAD.*?</header>',
        r'<div[^>]*class=["\']fad-header["\'][^>]*>.*?</div>',
        
        # Blocos de cabeçalho com script
        r'<!-- Cabeçalho institucional FAD -->.*?</script>',
        r'<!-- === Cabeçalho.*?</script>',
        
        # Timer de sessão específico
        r'<div[^>]*id=["\']session-status["\'][^>]*>.*?</script>',
        r'<!-- Bloco de status de sessão -->.*?</script>',
    ]
    
    # Aplicar substituições
    header_replaced = False
    for pattern in header_patterns:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            content = re.sub(pattern, '{% include "componentes/fad_header.html" %}', content, flags=re.DOTALL | re.IGNORECASE)
            header_replaced = True
            break
    
    # Se não encontrou padrão específico, tentar inserir após <body>
    if not header_replaced and '<body>' in content:
        content = content.replace('<body>', '<body>\n  {% include "componentes/fad_header.html" %}')
        header_replaced = True
    
    # Verificar se precisa adicionar context de sessão
    needs_session_context = any(keyword in content for keyword in [
        'painel-master', 'painel-coordenador', 'painel-analista',
        'usuario.nome', 'session', 'logout'
    ])
    
    if header_replaced:
        # Adicionar comentário de identificação
        comment = f"<!-- ✅ Template atualizado para usar fad_header.html padronizado -->\n"
        content = comment + content
        
        # Salvar arquivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_path.name} atualizado para usar fad_header.html")
        return True
    
    print(f"⚠️ {file_path.name} - nenhum cabeçalho identificado para substituir")
    return False

def process_authenticated_pages():
    """Processa páginas que precisam de autenticação"""
    
    # Páginas que precisam de autenticação
    authenticated_pages = [
        'pn_painel_usuario_master.html',
        'pn_painel_usuario_comum.html', 
        'pn_painel_usuario_adm.html',
        'pr_cadastro_projeto.html',
        'pr_conformidade_ambiental.html',
        'pr_dashboard_modulos.html',
        'pr_dashboard_projeto.html',
        'pr_favorabilidade_infraestrutural.html',
        'pr_favorabilidade_multicriterio.html',
        'pr_favorabilidade_socioeconomica.html',
        'meus_dados.html'
    ]
    
    templates_dir = Path("app/templates")
    updated_count = 0
    
    print("🔄 Iniciando atualização de páginas autenticadas...")
    print("="*60)
    
    for page_name in authenticated_pages:
        page_path = templates_dir / page_name
        
        if page_path.exists():
            # Criar backup
            backup_file(page_path)
            
            # Atualizar template
            if update_template_for_fad_header(page_path):
                updated_count += 1
        else:
            print(f"❌ Arquivo não encontrado: {page_name}")
    
    print("="*60)
    print(f"🎉 Atualização concluída!")
    print(f"📊 Páginas atualizadas: {updated_count}/{len(authenticated_pages)}")
    
    # Instruções para atualizar views
    print("\n📝 PRÓXIMOS PASSOS:")
    print("1. Atualizar views/endpoints para incluir contexto de sessão")
    print("2. Usar get_session_context(request) nos templates")
    print("3. Testar todas as páginas atualizadas")
    
    return updated_count

def update_view_functions():
    """Mostra exemplo de como atualizar funções de view"""
    example = '''
# ✅ Exemplo de como atualizar uma view para incluir contexto de sessão:

from app.core.session_control import get_session_context

@app.get("/painel-master", response_class=HTMLResponse)
def painel_master(request: Request):
    # Contexto de sessão
    session_context = get_session_context(request)
    
    # Contexto da página
    context = {
        "request": request,
        **session_context  # Inclui: usuario, tempo_restante, session_status
    }
    
    return templates.TemplateResponse("pn_painel_usuario_master.html", context)
'''
    
    print("\n" + "="*60)
    print("📋 EXEMPLO DE ATUALIZAÇÃO DE VIEWS:")
    print("="*60)
    print(example)

if __name__ == "__main__":
    try:
        updated = process_authenticated_pages()
        update_view_functions()
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        import traceback
        traceback.print_exc()
