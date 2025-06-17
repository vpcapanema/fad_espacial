#!/usr/bin/env python3
"""
Análise detalhada dos cabeçalhos nos templates
"""

import os
import re
from pathlib import Path

def analisar_cabecalho_detalhado(file_path):
    """Análise mais detalhada dos cabeçalhos"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        arquivo = Path(file_path).name
        
        # Verificar tipos específicos de cabeçalho
        if 'template_cabecalho_fad.html' in content:
            tipo = "FAD Padrão (template_cabecalho_fad.html)"
        elif 'fad_header.html' in content:
            tipo = "FAD Header (fad_header.html)"
        elif 'include' in content and 'header' in content.lower():
            tipo = "Include Personalizado"
        elif '<header' in content and 'fad' in content.lower():
            tipo = "Header FAD Próprio"
        elif '<header' in content:
            tipo = "Header Próprio"
        elif 'class="fad-header"' in content or 'fad-header' in content:
            tipo = "Classe FAD Header"
        else:
            tipo = "Sem Header Identificado"
        
        # Verificar login baseado em padrões mais específicos
        login = "Não"
        
        # Padrões específicos de login
        if any(pattern in content for pattern in [
            '{{ usuario.nome }}', 'usuario_id', 'session.get',
            'painel-master', 'painel-coordenador', 'painel-analista',
            'request.session', 'Bem-vindo(a)', 'usuario.tipo'
        ]):
            login = "Sim"
        
        # Exceções específicas
        if arquivo.lower() in ['au_login.html', 'home.html', 'cadastro_usuario.html', 
                              'mapa_rotas_fad_atualizado.html', 'pagina_em_construcao.html']:
            login = "Não"
            
        return {
            'arquivo': arquivo,
            'cabecalho': tipo,
            'login': login,
            'path': str(file_path)
        }
        
    except Exception as e:
        return {
            'arquivo': Path(file_path).name,
            'cabecalho': f"ERRO: {e}",
            'login': "ERRO",
            'path': str(file_path)
        }

def main():
    templates_dir = Path("app/templates")
    resultados = []
    
    # Buscar todos os arquivos HTML
    for html_file in templates_dir.rglob("*.html"):
        resultado = analisar_cabecalho_detalhado(html_file)
        resultados.append(resultado)
    
    # Ordenar por nome do arquivo
    resultados.sort(key=lambda x: x['arquivo'])
    
    # Criar tabela markdown
    print("\n## 📋 ANÁLISE COMPLETA DOS TEMPLATES HTML")
    print("\n| ARQUIVO | TIPO DE CABEÇALHO | PRECISA LOGIN |")
    print("|---------|-------------------|---------------|")
    
    for resultado in resultados:
        arquivo = resultado['arquivo']
        cabecalho = resultado['cabecalho']
        login = resultado['login']
        print(f"| {arquivo} | {cabecalho} | {login} |")
    
    # Estatísticas resumidas
    print(f"\n### 📊 ESTATÍSTICAS")
    
    fad_padrao = sum(1 for r in resultados if 'template_cabecalho_fad.html' in r['cabecalho'])
    fad_header = sum(1 for r in resultados if 'fad_header.html' in r['cabecalho'])
    header_proprio = sum(1 for r in resultados if 'Header Próprio' in r['cabecalho'])
    sem_header = sum(1 for r in resultados if 'Sem Header' in r['cabecalho'])
    com_login = sum(1 for r in resultados if r['login'] == 'Sim')
    
    print(f"- **Total de arquivos:** {len(resultados)}")
    print(f"- **FAD Padrão (template_cabecalho_fad.html):** {fad_padrao}")
    print(f"- **FAD Header (fad_header.html):** {fad_header}")  
    print(f"- **Header Próprio:** {header_proprio}")
    print(f"- **Sem Header Identificado:** {sem_header}")
    print(f"- **Precisam Login:** {com_login}")
    
    # Listar arquivos que usam FAD Padrão
    fad_padrao_files = [r['arquivo'] for r in resultados if 'template_cabecalho_fad.html' in r['cabecalho']]
    if fad_padrao_files:
        print(f"\n### 🎯 ARQUIVOS QUE USAM FAD PADRÃO:")
        for arquivo in fad_padrao_files:
            print(f"- {arquivo}")
    else:
        print(f"\n### ⚠️ NENHUM ARQUIVO USA O template_cabecalho_fad.html")
    
    # Listar arquivos que usam fad_header.html
    fad_header_files = [r['arquivo'] for r in resultados if 'fad_header.html' in r['cabecalho']]
    if fad_header_files:
        print(f"\n### 🎯 ARQUIVOS QUE USAM fad_header.html:")
        for arquivo in fad_header_files:
            print(f"- {arquivo}")

if __name__ == "__main__":
    main()
