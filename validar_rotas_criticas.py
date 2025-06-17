#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VALIDADOR DE ROTAS CRÍTICAS - FAD
========================================
Data: 17/06/2025
Sistema: Ferramenta de Análise Dinamizada

Este script valida se todas as rotas críticas estão funcionando corretamente.
Execute este script antes e depois de qualquer alteração no main.py

Uso: python validar_rotas_criticas.py
"""

import requests
import sys
import json
from datetime import datetime

# 🎯 CONFIGURAÇÕES
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# 📋 ROTAS CRÍTICAS PARA VALIDAÇÃO
ROTAS_CRITICAS = [
    {
        "nome": "Homepage",
        "url": "/",
        "metodo": "GET",
        "status_esperado": 200,
        "critico": False
    },
    {
        "nome": "Login Page", 
        "url": "/login",
        "metodo": "GET",
        "status_esperado": 200,
        "critico": True
    },
    {
        "nome": "Painel Master (Redirect)",
        "url": "/painel-master/",
        "metodo": "GET", 
        "status_esperado": [200, 302],  # 302 = redirect para login (esperado)
        "critico": True
    },
    {
        "nome": "Dados Analistas",
        "url": "/painel-master/dados/analistas",
        "metodo": "GET",
        "status_esperado": 200,
        "critico": True
    },
    {
        "nome": "Auditoria PF",
        "url": "/painel-master/auditoria/pessoa-fisica/1",
        "metodo": "GET",
        "status_esperado": [200, 404],  # 404 se ID não existir (ok)
        "critico": True
    },
    {
        "nome": "Exportação PF",
        "url": "/painel-master/exportar/pessoa-fisica/1/csv",
        "metodo": "GET", 
        "status_esperado": [200, 404],  # 404 se ID não existir (ok)
        "critico": True
    }
]

def validar_rota(rota):
    """Valida uma rota específica"""
    try:
        url_completa = BASE_URL + rota["url"]
        
        if rota["metodo"] == "GET":
            response = requests.get(url_completa, timeout=TIMEOUT, allow_redirects=False)
        elif rota["metodo"] == "POST":
            response = requests.post(url_completa, timeout=TIMEOUT, allow_redirects=False)
        else:
            return False, f"Método {rota['metodo']} não suportado"
        
        # Verificar status code
        status_esperado = rota["status_esperado"]
        if isinstance(status_esperado, list):
            status_ok = response.status_code in status_esperado
        else:
            status_ok = response.status_code == status_esperado
            
        if status_ok:
            return True, f"✅ Status {response.status_code}"
        else:
            return False, f"❌ Status {response.status_code} (esperado: {status_esperado})"
            
    except requests.exceptions.ConnectionError:
        return False, "❌ Servidor não está rodando"
    except requests.exceptions.Timeout:
        return False, "❌ Timeout na requisição"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def executar_validacao():
    """Executa a validação completa"""
    print("🔍 VALIDADOR DE ROTAS CRÍTICAS - FAD")
    print("=" * 50)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Servidor: {BASE_URL}")
    print("=" * 50)
    
    resultados = []
    total_rotas = len(ROTAS_CRITICAS)
    rotas_ok = 0
    rotas_criticas_ok = 0
    total_criticas = sum(1 for r in ROTAS_CRITICAS if r["critico"])
    
    for i, rota in enumerate(ROTAS_CRITICAS, 1):
        print(f"\n[{i}/{total_rotas}] Testando: {rota['nome']}")
        print(f"    URL: {rota['url']}")
        
        sucesso, mensagem = validar_rota(rota)
        
        print(f"    Resultado: {mensagem}")
        
        if sucesso:
            rotas_ok += 1
            if rota["critico"]:
                rotas_criticas_ok += 1
        
        resultados.append({
            "nome": rota["nome"],
            "url": rota["url"], 
            "critico": rota["critico"],
            "sucesso": sucesso,
            "mensagem": mensagem
        })
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO FINAL")
    print("=" * 50)
    print(f"Total de rotas testadas: {total_rotas}")
    print(f"Rotas funcionais: {rotas_ok}/{total_rotas}")
    print(f"Rotas críticas funcionais: {rotas_criticas_ok}/{total_criticas}")
    
    # Status geral
    if rotas_criticas_ok == total_criticas:
        status_geral = "✅ SISTEMA FUNCIONANDO CORRETAMENTE"
        codigo_saida = 0
    else:
        status_geral = "⚠️  PROBLEMAS DETECTADOS NAS ROTAS CRÍTICAS"
        codigo_saida = 1
    
    print(f"\nStatus Geral: {status_geral}")
    
    # Listar problemas
    problemas = [r for r in resultados if not r["sucesso"] and r["critico"]]
    if problemas:
        print("\n❌ ROTAS CRÍTICAS COM PROBLEMAS:")
        for p in problemas:
            print(f"   - {p['nome']}: {p['mensagem']}")
    
    # Salvar relatório
    relatorio = {
        "data_validacao": datetime.now().isoformat(),
        "servidor": BASE_URL,
        "total_rotas": total_rotas,
        "rotas_ok": rotas_ok, 
        "rotas_criticas_ok": rotas_criticas_ok,
        "total_criticas": total_criticas,
        "status_geral": status_geral,
        "resultados": resultados
    }
    
    with open("relatorio_validacao_rotas.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: relatorio_validacao_rotas.json")
    
    return codigo_saida

if __name__ == "__main__":
    try:
        codigo_saida = executar_validacao()
        sys.exit(codigo_saida)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {str(e)}")
        sys.exit(1)
