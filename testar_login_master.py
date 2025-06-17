#!/usr/bin/env python3
"""
Script para testar login como master
"""

import requests
import json

def testar_login_master():
    print("🔧 Testando login como master...")
    
    # URL do login
    url = "http://127.0.0.1:8000/login"
    
    # Dados do formulário
    dados = {
        'email': 'vpcapanema@der.sp.gov.br',
        'senha': 'Malditas131533*',
        'tipo': 'master'
    }
    
    # Fazer requisição
    response = requests.post(url, data=dados)
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    
    if response.status_code == 200:
        resposta_json = response.json()
        if 'redirect' in resposta_json:
            print(f"✅ Login bem-sucedido! Redirecionamento para: {resposta_json['redirect']}")
        else:
            print("⚠️ Login bem-sucedido, mas sem redirecionamento")
    else:
        print("❌ Falha no login")

if __name__ == "__main__":
    testar_login_master()
