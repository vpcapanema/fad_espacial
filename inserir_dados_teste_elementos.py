#!/usr/bin/env python3
"""
Script para inserir dados de teste nas tabelas de elementos rodoviários
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.cd_trecho_estadualizacao import TrechoEstadualizacao
from app.models.cd_rodovia_estadualizacao import RodoviaEstadualizacao  
from app.models.cd_dispositivo_estadualizacao import DispositivoEstadualizacao
from app.models.cd_obra_arte_estadualizacao import ObraArteEstadualizacao
from datetime import datetime

def inserir_dados_teste():
    db = SessionLocal()
    
    try:
        print("🚀 Iniciando inserção de dados de teste...")
        
        # ==================== TRECHOS RODOVIÁRIOS ====================
        print("\n📍 Inserindo Trechos Rodoviários...")
        
        trechos = [
            TrechoEstadualizacao(
                codigo="TR-001",
                denominacao="Trecho São Paulo - Campinas", 
                tipo="Rodovia Federal",
                municipio="São Paulo",
                extensao_km=98.5,
                criado_em=datetime.now()
            ),
            TrechoEstadualizacao(
                codigo="TR-002", 
                denominacao="Trecho Rio - Petrópolis",
                tipo="Rodovia Estadual",
                municipio="Rio de Janeiro", 
                extensao_km=65.2,
                criado_em=datetime.now()
            ),
            TrechoEstadualizacao(
                codigo="TR-003",
                denominacao="Trecho Belo Horizonte - Contagem",
                tipo="Rodovia Municipal", 
                municipio="Belo Horizonte",
                extensao_km=23.8,
                criado_em=datetime.now()
            )
        ]
        
        for trecho in trechos:
            db.add(trecho)
        
        # ==================== RODOVIAS ====================
        print("🛣️ Inserindo Rodovias...")
        
        rodovias = [
            RodoviaEstadualizacao(
                codigo="BR-101", 
                denominacao="Rodovia Rio-Santos",
                tipo="Federal",
                municipio="Santos",
                extensao_km=125.4,
                criado_em=datetime.now()
            ),
            RodoviaEstadualizacao(
                codigo="SP-348",
                denominacao="Rodovia dos Bandeirantes", 
                tipo="Estadual",
                municipio="São Paulo",
                extensao_km=201.3,
                criado_em=datetime.now()
            ),
            RodoviaEstadualizacao(
                codigo="RJ-104",
                denominacao="Linha Vermelha",
                tipo="Estadual", 
                municipio="Rio de Janeiro",
                extensao_km=58.7,
                criado_em=datetime.now()
            )
        ]
        
        for rodovia in rodovias:
            db.add(rodovia)
            
        # ==================== DISPOSITIVOS ====================
        print("⚙️ Inserindo Dispositivos...")
        
        dispositivos = [
            DispositivoEstadualizacao(
                codigo="DV-001",
                denominacao="Viaduto do Chá",
                tipo="Viaduto",
                municipio="São Paulo", 
                extensao_km=0.8,
                criado_em=datetime.now()
            ),
            DispositivoEstadualizacao(
                codigo="DV-002",
                denominacao="Túnel Rebouças", 
                tipo="Túnel",
                municipio="Rio de Janeiro",
                extensao_km=2.9,
                criado_em=datetime.now()
            ),
            DispositivoEstadualizacao(
                codigo="DV-003",
                denominacao="Rotatória Central",
                tipo="Rotatória",
                municipio="Campinas",
                extensao_km=0.2,
                criado_em=datetime.now()
            )
        ]
        
        for dispositivo in dispositivos:
            db.add(dispositivo)
            
        # ==================== OBRAS DE ARTE ====================
        print("🌉 Inserindo Obras de Arte...")
        
        obras_arte = [
            ObraArteEstadualizacao(
                codigo="OA-001",
                denominacao="Ponte Estaiada",
                tipo="Ponte Estaiada", 
                municipio="São Paulo",
                extensao_km=0.14,
                criado_em=datetime.now()
            ),
            ObraArteEstadualizacao(
                codigo="OA-002",
                denominacao="Ponte Rio-Niterói",
                tipo="Ponte", 
                municipio="Rio de Janeiro",
                extensao_km=13.29,
                criado_em=datetime.now()
            ),
            ObraArteEstadualizacao(
                codigo="OA-003", 
                denominacao="Viaduto Santa Tereza",
                tipo="Viaduto",
                municipio="Belo Horizonte",
                extensao_km=0.52,
                criado_em=datetime.now()
            )
        ]
        
        for obra in obras_arte:
            db.add(obra)
            
        # Commit das mudanças
        db.commit()
        print("\n✅ Dados de teste inseridos com sucesso!")
        
        # Verificação
        print("\n📊 Verificando inserções:")
        print(f"Trechos: {db.query(TrechoEstadualizacao).count()}")
        print(f"Rodovias: {db.query(RodoviaEstadualizacao).count()}")
        print(f"Dispositivos: {db.query(DispositivoEstadualizacao).count()}")
        print(f"Obras de Arte: {db.query(ObraArteEstadualizacao).count()}")
        
    except Exception as e:
        print(f"❌ Erro durante a inserção: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    inserir_dados_teste()
