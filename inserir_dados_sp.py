#!/usr/bin/env python3
"""
Script para inserir dados de teste de elementos rodoviários de São Paulo
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

def limpar_dados_existentes(db):
    """Remove dados de teste existentes"""
    print("🧹 Limpando dados existentes...")
    db.query(TrechoEstadualizacao).delete()
    db.query(RodoviaEstadualizacao).delete()
    db.query(DispositivoEstadualizacao).delete()
    db.query(ObraArteEstadualizacao).delete()
    db.commit()

def inserir_dados_sao_paulo():
    db = SessionLocal()
    
    try:
        print("🚀 Iniciando inserção de dados de São Paulo...")
        
        # Limpar dados existentes
        limpar_dados_existentes(db)
        
        # ==================== RODOVIAS DE SÃO PAULO ====================
        print("\n🛣️ Inserindo Rodovias de São Paulo...")
        
        rodovias = [
            # Rodovias Radiais (SP-xxx)
            RodoviaEstadualizacao(
                codigo="SP-348",
                denominacao="Rodovia dos Bandeirantes", 
                tipo="Radial",
                municipio="São Paulo",
                extensao_km=201.3,
                criado_em=datetime.now()
            ),
            RodoviaEstadualizacao(
                codigo="SP-280",
                denominacao="Rodovia Castello Branco",
                tipo="Radial", 
                municipio="São Paulo",
                extensao_km=173.8,
                criado_em=datetime.now()
            ),
            # Rodovia de Acesso (SPA-xxx)
            RodoviaEstadualizacao(
                codigo="SPA-050",
                denominacao="Rodovia de Acesso Anhanguera",
                tipo="Acesso",
                municipio="São Paulo",
                extensao_km=45.2,
                criado_em=datetime.now()
            ),
            # Rodovia de Interligação (SPI-xxx)
            RodoviaEstadualizacao(
                codigo="SPI-070",
                denominacao="Rodovia Ayrton Senna",
                tipo="Interligação",
                municipio="Guarulhos", 
                extensao_km=22.5,
                criado_em=datetime.now()
            ),
            # Rodovia Marginal (SPM-xxx)
            RodoviaEstadualizacao(
                codigo="SPM-015",
                denominacao="Marginal Tietê",
                tipo="Marginal",
                municipio="São Paulo",
                extensao_km=28.7,
                criado_em=datetime.now()
            )
        ]
        
        for rodovia in rodovias:
            db.add(rodovia)
        
        # ==================== TRECHOS RODOVIÁRIOS DE SÃO PAULO ====================
        print("📍 Inserindo Trechos Rodoviários de São Paulo...")
        
        trechos = [
            TrechoEstadualizacao(
                codigo="TR-SP-001",
                denominacao="Trecho São Paulo - Jundiaí (Via Anhanguera)", 
                tipo="Trecho Estadual",
                municipio="São Paulo",
                extensao_km=58.3,
                criado_em=datetime.now()
            ),
            TrechoEstadualizacao(
                codigo="TR-SP-002", 
                denominacao="Trecho Campinas - Sorocaba (Via Castello Branco)",
                tipo="Trecho Estadual",
                municipio="Campinas", 
                extensao_km=87.4,
                criado_em=datetime.now()
            ),
            TrechoEstadualizacao(
                codigo="TR-SP-003",
                denominacao="Trecho São Bernardo - Santo André (Via Anchieta)",
                tipo="Trecho Metropolitano", 
                municipio="São Bernardo do Campo",
                extensao_km=15.6,
                criado_em=datetime.now()
            ),
            TrechoEstadualizacao(
                codigo="TR-SP-004",
                denominacao="Trecho Osasco - Barueri (Via Castello Branco)",
                tipo="Trecho Metropolitano",
                municipio="Osasco",
                extensao_km=12.8,
                criado_em=datetime.now()
            )
        ]
        
        for trecho in trechos:
            db.add(trecho)
            
        # ==================== DISPOSITIVOS DE SÃO PAULO ====================
        print("⚙️ Inserindo Dispositivos de São Paulo...")
        
        dispositivos = [
            DispositivoEstadualizacao(
                codigo="DV-SP-001",
                denominacao="Viaduto do Chá",
                tipo="Viaduto",
                municipio="São Paulo", 
                extensao_km=0.24,
                criado_em=datetime.now()
            ),
            DispositivoEstadualizacao(
                codigo="DV-SP-002",
                denominacao="Túnel Jânio Quadros", 
                tipo="Túnel",
                municipio="São Paulo",
                extensao_km=1.8,
                criado_em=datetime.now()
            ),
            DispositivoEstadualizacao(
                codigo="DV-SP-003",
                denominacao="Complexo Viário Heróis de 1932",
                tipo="Complexo Viário",
                municipio="São Paulo",
                extensao_km=2.1,
                criado_em=datetime.now()
            ),
            DispositivoEstadualizacao(
                codigo="DV-SP-004",
                denominacao="Rotatória do Ibirapuera",
                tipo="Rotatória",
                municipio="São Paulo",
                extensao_km=0.3,
                criado_em=datetime.now()
            )
        ]
        
        for dispositivo in dispositivos:
            db.add(dispositivo)
            
        # ==================== OBRAS DE ARTE DE SÃO PAULO ====================
        print("🌉 Inserindo Obras de Arte de São Paulo...")
        
        obras_arte = [
            ObraArteEstadualizacao(
                codigo="OA-SP-001",
                denominacao="Ponte Estaiada Octavio Frias de Oliveira",
                tipo="Ponte Estaiada", 
                municipio="São Paulo",
                extensao_km=0.14,
                criado_em=datetime.now()
            ),
            ObraArteEstadualizacao(
                codigo="OA-SP-002",
                denominacao="Ponte das Bandeiras",
                tipo="Ponte", 
                municipio="São Paulo",
                extensao_km=0.32,
                criado_em=datetime.now()
            ),
            ObraArteEstadualizacao(
                codigo="OA-SP-003", 
                denominacao="Viaduto Santa Ifigênia",
                tipo="Viaduto",
                municipio="São Paulo",
                extensao_km=0.24,
                criado_em=datetime.now()
            ),
            ObraArteEstadualizacao(
                codigo="OA-SP-004",
                denominacao="Ponte Cidade Jardim",
                tipo="Ponte",
                municipio="São Paulo",
                extensao_km=0.18,
                criado_em=datetime.now()
            ),
            ObraArteEstadualizacao(
                codigo="OA-SP-005",
                denominacao="Viaduto do Gasômetro",
                tipo="Viaduto",
                municipio="São Paulo", 
                extensao_km=0.28,
                criado_em=datetime.now()
            )
        ]
        
        for obra in obras_arte:
            db.add(obra)
            
        # Commit das mudanças
        db.commit()
        print("\n✅ Dados de São Paulo inseridos com sucesso!")
        
        # Verificação
        print("\n📊 Verificando inserções:")
        print(f"Rodovias: {db.query(RodoviaEstadualizacao).count()}")
        print(f"Trechos: {db.query(TrechoEstadualizacao).count()}")
        print(f"Dispositivos: {db.query(DispositivoEstadualizacao).count()}")
        print(f"Obras de Arte: {db.query(ObraArteEstadualizacao).count()}")
        
        # Mostrar detalhes das rodovias por tipo
        print("\n🛣️ Rodovias por tipo:")
        for tipo in ["Radial", "Acesso", "Interligação", "Marginal"]:
            count = db.query(RodoviaEstadualizacao).filter(RodoviaEstadualizacao.tipo == tipo).count()
            print(f"  {tipo}: {count}")
        
    except Exception as e:
        print(f"❌ Erro durante a inserção: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    inserir_dados_sao_paulo()
