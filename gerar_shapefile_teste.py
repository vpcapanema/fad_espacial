#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar um shapefile de teste válido para o sistema FAD-GEO
Cria um trecho rodoviário fictício com geometria LineString
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
import zipfile
import os
from pathlib import Path

def criar_shapefile_teste():
    """Cria um shapefile de teste com um trecho rodoviário fictício"""
    
    # Coordenadas de exemplo (região de Brasília/DF)
    # Simulando um trecho rodoviário entre dois pontos
    coordenadas = [
        (-47.8826, -15.7942),  # Início (próximo ao Plano Piloto)
        (-47.8800, -15.7950),  # Ponto intermediário 1
        (-47.8750, -15.7960),  # Ponto intermediário 2
        (-47.8700, -15.7970),  # Ponto intermediário 3
        (-47.8650, -15.7980),  # Fim
    ]
    
    # Criar geometria LineString
    linha = LineString(coordenadas)
    
    # Criar GeoDataFrame com atributos típicos de um trecho rodoviário
    dados = {
        'id_trecho': [1],
        'nome': ['BR-040 - Trecho Teste'],
        'rodovia': ['BR-040'],
        'uf': ['DF'],
        'municipio': ['Brasília'],
        'extensao_km': [2.5],
        'tipo': ['Rodovia Federal'],
        'estado_conservacao': ['Bom'],
        'geometry': [linha]
    }
    
    # Criar GeoDataFrame
    gdf = gpd.GeoDataFrame(dados, crs='EPSG:4326')
    
    return gdf

def gerar_zip_shapefile():
    """Gera o shapefile e compacta em ZIP"""
    
    print("🔄 Gerando shapefile de teste...")
    
    # Criar diretório temporário
    temp_dir = Path("temp_shapefile")
    temp_dir.mkdir(exist_ok=True)
    
    # Gerar shapefile
    gdf = criar_shapefile_teste()
    
    # Nome base do arquivo
    nome_base = "trecho_rodoviario_teste"
    caminho_shp = temp_dir / nome_base
    
    # Salvar shapefile (gera automaticamente .shp, .shx, .dbf, .prj)
    gdf.to_file(caminho_shp.with_suffix('.shp'))
    
    print(f"✅ Shapefile criado: {caminho_shp}.shp")
    
    # Listar arquivos gerados
    arquivos_shp = list(temp_dir.glob(f"{nome_base}.*"))
    print(f"📁 Arquivos gerados: {[f.name for f in arquivos_shp]}")
    
    # Criar ZIP
    nome_zip = "trecho_rodoviario_teste.zip"
    with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arquivo in arquivos_shp:
            zipf.write(arquivo, arquivo.name)
            print(f"➕ Adicionado ao ZIP: {arquivo.name}")
    
    # Limpar arquivos temporários
    for arquivo in arquivos_shp:
        arquivo.unlink()
    temp_dir.rmdir()
    
    print(f"🎯 ZIP criado com sucesso: {nome_zip}")
    print(f"📍 Localização: {os.path.abspath(nome_zip)}")
    
    # Verificar conteúdo do ZIP
    print("\n📋 Conteúdo do ZIP:")
    with zipfile.ZipFile(nome_zip, 'r') as zipf:
        for info in zipf.infolist():
            print(f"   - {info.filename} ({info.file_size} bytes)")
    
    return nome_zip

def validar_zip_criado(nome_zip):
    """Valida se o ZIP contém todos os arquivos necessários"""
    extensoes_obrigatorias = {'.shp', '.shx', '.dbf', '.prj'}
    
    print(f"\n🔍 Validando ZIP: {nome_zip}")
    
    with zipfile.ZipFile(nome_zip, 'r') as zipf:
        arquivos = {Path(f).suffix.lower() for f in zipf.namelist()}
        
    print(f"📁 Extensões encontradas: {sorted(arquivos)}")
    print(f"📋 Extensões obrigatórias: {sorted(extensoes_obrigatorias)}")
    
    if extensoes_obrigatorias.issubset(arquivos):
        print("✅ ZIP válido! Contém todos os arquivos obrigatórios do shapefile.")
        return True
    else:
        faltando = extensoes_obrigatorias - arquivos
        print(f"❌ ZIP inválido! Faltando: {sorted(faltando)}")
        return False

if __name__ == "__main__":
    try:
        # Verificar dependências
        print("🔍 Verificando dependências...")
        import geopandas
        import shapely
        print("✅ GeoPandas e Shapely disponíveis")
        
        # Gerar ZIP
        nome_zip = gerar_zip_shapefile()
        
        # Validar
        validar_zip_criado(nome_zip)
        
        print(f"\n🎉 SUCESSO! Arquivo pronto para teste: {nome_zip}")
        print("💡 Você pode usar este arquivo para testar o upload no sistema FAD-GEO")
        
    except ImportError as e:
        print(f"❌ Erro de dependência: {e}")
        print("💡 Instale as dependências: pip install geopandas shapely")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
