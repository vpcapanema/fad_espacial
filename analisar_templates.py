#!/usr/bin/env python3
"""
Script para analisar templates HTML e verificar tipo de cabeçalho e necessidade de login
"""

import os
import re
from pathlib import Path

def analisar_template(file_path):
    """Analisa um template HTML para identificar tipo de cabeçalho e necessidade de login"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar tipo de cabeçalho
        cabecalho_tipo = "Próprio"
        
        # Verificar se inclui template_cabecalho_fad.html
        if 'template_cabecalho_fad.html' in content:
            cabecalho_tipo = "FAD Padrão"
        elif 'fad_header.html' in content:
            cabecalho_tipo = "FAD Header"
        elif '{% include' in content and 'cabecalho' in content.lower():
            cabecalho_tipo = "Include Personalizado"
        elif '<header' in content or 'fad-header' in content:
            cabecalho_tipo = "Próprio"
        
        # Verificar necessidade de login
        precisa_login = "Não"
        
        # Padrões que indicam necessidade de login
        login_patterns = [
            r'usuario\.', r'request\.session', r'session\.get',
            r'@login_required', r'usuario_id', r'usuario_tipo',
            r'if.*usuario', r'Bem-vindo.*usuario', r'painel.*usuario'
        ]
        
        for pattern in login_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                precisa_login = "Sim"
                break
        
        # Verificações específicas para certas páginas
        nome_arquivo = Path(file_path).name.lower()
        
        if any(x in nome_arquivo for x in ['login', 'home', 'cadastro_usuario', 'recuperar', 'mapa_rotas']):
            precisa_login = "Não"
        elif any(x in nome_arquivo for x in ['painel', 'dashboard', 'meus_dados']):
            precisa_login = "Sim"
        elif 'conformidade' in nome_arquivo or 'favorabilidade' in nome_arquivo:
            precisa_login = "Sim"
            
        return {
            'arquivo': Path(file_path).name,
            'cabecalho': cabecalho_tipo,
            'login': precisa_login
        }
        
    except Exception as e:
        return {
            'arquivo': Path(file_path).name,
            'cabecalho': f"ERRO: {e}",
            'login': "ERRO"
        }

def main():
    templates_dir = Path("app/templates")
    resultados = []
    
    # Buscar todos os arquivos HTML
    for html_file in templates_dir.rglob("*.html"):
        resultado = analisar_template(html_file)
        resultados.append(resultado)
    
    # Ordenar por nome do arquivo
    resultados.sort(key=lambda x: x['arquivo'])
    
    # Imprimir tabela
    print("\n" + "="*80)
    print("ANÁLISE DE TEMPLATES HTML - CABEÇALHOS E LOGIN")
    print("="*80)
    print(f"{'ARQUIVO':<40} {'CABEÇALHO':<20} {'PRECISA LOGIN':<15}")
    print("-"*80)
    
    for resultado in resultados:
        print(f"{resultado['arquivo']:<40} {resultado['cabecalho']:<20} {resultado['login']:<15}")
    
    print("-"*80)
    print(f"Total de arquivos analisados: {len(resultados)}")
    
    # Estatísticas
    fad_padrao = sum(1 for r in resultados if r['cabecalho'] == 'FAD Padrão')
    fad_header = sum(1 for r in resultados if r['cabecalho'] == 'FAD Header')
    proprio = sum(1 for r in resultados if r['cabecalho'] == 'Próprio')
    com_login = sum(1 for r in resultados if r['login'] == 'Sim')
    
    print(f"\nESTATÍSTICAS:")
    print(f"- FAD Padrão: {fad_padrao}")
    print(f"- FAD Header: {fad_header}")
    print(f"- Próprio: {proprio}")
    print(f"- Precisam Login: {com_login}")
    print("="*80)

if __name__ == "__main__":
    main()
