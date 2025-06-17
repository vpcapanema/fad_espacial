#!/usr/bin/env python3
"""
Script para corrigir e gerar PDFs dos formulários
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

import pdfkit

def gerar_pdf_corrigido(html_path, pdf_path):
    """Gera PDF com configuração corrigida para evitar erros de rede"""
    try:
        # Configuração corrigida para evitar erros de protocolo
        options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'dpi': 300,
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'disable-external-links': None,
            'disable-javascript': None,  # Desabilitar JS para evitar erros de rede
            'no-images': None,  # Desabilitar imagens externas
            'disable-plugins': None,
            'load-error-handling': 'ignore',
            'load-media-error-handling': 'ignore',
            'quiet': None
        }
        
        pdfkit.from_file(html_path, pdf_path, options=options)
        return True
        
    except Exception as e:
        print(f"❌ Erro pdfkit: {e}")
        return False

def main():
    print("🔧 Corrigindo geração de PDFs...")
    
    # Caminhos dos HTMLs gerados
    base_dir = Path("c:/Users/vinic/fad-geo/formularios_cadastro_usuarios/vpcapanema_20250616")
    
    arquivos = [
        ("tipo_coordenador/2_coordenador_20250616_v1.html", "ID 2 - Coordenador"),
        ("tipo_analista/4_analista_20250616_v1.html", "ID 4 - Analista"), 
        ("tipo_master/5_master_20250616_v1.html", "ID 5 - Master")
    ]
    
    for arquivo_html, descricao in arquivos:
        print(f"\n📑 Processando {descricao}...")
        
        html_path = base_dir / arquivo_html
        pdf_path = str(html_path).replace('.html', '.pdf')
        
        if not html_path.exists():
            print(f"❌ HTML não encontrado: {html_path}")
            continue
            
        print(f"   📄 HTML: {html_path}")
        print(f"   📑 PDF: {pdf_path}")
        
        if gerar_pdf_corrigido(str(html_path), pdf_path):
            if os.path.exists(pdf_path):
                tamanho = os.path.getsize(pdf_path)
                print(f"   ✅ PDF gerado com sucesso! ({tamanho:,} bytes)")
            else:
                print(f"   ❌ PDF não foi criado")
        else:
            print(f"   ❌ Falha na geração do PDF")
    
    print("\n🏁 Processo de correção finalizado!")

if __name__ == "__main__":
    main()
