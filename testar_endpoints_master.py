#!/usr/bin/env python3
"""
Teste rápido dos endpoints do painel master
"""

import requests
import json

def testar_endpoints():
    print("🔧 Testando endpoints do painel master...")
    
    base_url = "http://127.0.0.1:8000/painel-master"
    
    endpoints = [
        "/dados/analistas",
        "/dados/todos-usuarios", 
        "/dados/pessoas-fisicas",
        "/dados/pessoas-juridicas",
        "/dados/trechos-estadualizacao",
        "/dados/trechos-rodoviarios",
        "/dados/rodovias",
        "/dados/dispositivos",
        "/dados/obras-arte"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"   Erro: {response.text}")
        except Exception as e:
            print(f"❌ {endpoint}: Erro - {e}")

if __name__ == "__main__":
    testar_endpoints()
