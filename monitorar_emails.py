#!/usr/bin/env python3
"""
Sistema de Monitoramento de Logs de Email - FAD
Monitora e analisa logs de envio de emails do sistema
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Optional

class EmailLogMonitor:
    """Monitor de logs de email do sistema FAD"""
    
    def __init__(self, log_dir: str = "logs/emails"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.log_dir / "email_logs.db"
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados de logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_email VARCHAR(50) NOT NULL,
                destinatario VARCHAR(255) NOT NULL,
                remetente VARCHAR(255) NOT NULL,
                assunto TEXT,
                status VARCHAR(20) NOT NULL,
                erro TEXT,
                tamanho_anexo INTEGER,
                ip_origem VARCHAR(45),
                user_agent TEXT,
                tempo_processamento_ms INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estatisticas_diarias (
                data DATE PRIMARY KEY,
                total_enviados INTEGER DEFAULT 0,
                total_falhados INTEGER DEFAULT 0,
                emails_recuperacao INTEGER DEFAULT 0,
                emails_cadastro INTEGER DEFAULT 0,
                tempo_medio_ms REAL DEFAULT 0,
                ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def registrar_envio(
        self,
        tipo_email: str,
        destinatario: str,
        remetente: str,
        assunto: str,
        status: str,
        erro: Optional[str] = None,
        tamanho_anexo: Optional[int] = None,
        ip_origem: Optional[str] = None,
        user_agent: Optional[str] = None,
        tempo_processamento_ms: Optional[int] = None
    ):
        """Registra um envio de email no log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO email_logs 
            (tipo_email, destinatario, remetente, assunto, status, erro, 
             tamanho_anexo, ip_origem, user_agent, tempo_processamento_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tipo_email, destinatario, remetente, assunto, status, erro,
            tamanho_anexo, ip_origem, user_agent, tempo_processamento_ms
        ))
        
        conn.commit()
        conn.close()
        
        # Atualiza estatísticas diárias
        self._atualizar_estatisticas_diarias()
    
    def _atualizar_estatisticas_diarias(self):
        """Atualiza as estatísticas diárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        hoje = datetime.now().date()
        
        # Calcula estatísticas do dia
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'sucesso' THEN 1 ELSE 0 END) as enviados,
                SUM(CASE WHEN status = 'erro' THEN 1 ELSE 0 END) as falhados,
                SUM(CASE WHEN tipo_email = 'recuperacao_senha' THEN 1 ELSE 0 END) as recuperacao,
                SUM(CASE WHEN tipo_email = 'confirmacao_cadastro' THEN 1 ELSE 0 END) as cadastro,
                AVG(CASE WHEN tempo_processamento_ms IS NOT NULL THEN tempo_processamento_ms ELSE 0 END) as tempo_medio
            FROM email_logs 
            WHERE DATE(timestamp) = ?
        """, (hoje,))
        
        resultado = cursor.fetchone()
        total, enviados, falhados, recuperacao, cadastro, tempo_medio = resultado
        
        # Insere ou atualiza estatísticas
        cursor.execute("""
            INSERT OR REPLACE INTO estatisticas_diarias 
            (data, total_enviados, total_falhados, emails_recuperacao, 
             emails_cadastro, tempo_medio_ms, ultima_atualizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (hoje, enviados, falhados, recuperacao, cadastro, tempo_medio, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def obter_estatisticas_periodo(self, dias: int = 7) -> Dict:
        """Obtém estatísticas dos últimos N dias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_inicio = datetime.now().date() - timedelta(days=dias)
        
        cursor.execute("""
            SELECT 
                SUM(total_enviados) as total_enviados,
                SUM(total_falhados) as total_falhados,
                SUM(emails_recuperacao) as emails_recuperacao,
                SUM(emails_cadastro) as emails_cadastro,
                AVG(tempo_medio_ms) as tempo_medio_ms,
                COUNT(*) as dias_com_atividade
            FROM estatisticas_diarias 
            WHERE data >= ?
        """, (data_inicio,))
        
        resultado = cursor.fetchone()
        
        # Obtém detalhes por dia
        cursor.execute("""
            SELECT data, total_enviados, total_falhados, emails_recuperacao, emails_cadastro
            FROM estatisticas_diarias 
            WHERE data >= ?
            ORDER BY data DESC
        """, (data_inicio,))
        
        detalhes_diarios = cursor.fetchall()
        
        conn.close()
        
        return {
            'periodo_dias': dias,
            'total_enviados': resultado[0] or 0,
            'total_falhados': resultado[1] or 0,
            'emails_recuperacao': resultado[2] or 0,
            'emails_cadastro': resultado[3] or 0,
            'tempo_medio_ms': resultado[4] or 0,
            'dias_com_atividade': resultado[5] or 0,
            'taxa_sucesso': ((resultado[0] or 0) / max(1, (resultado[0] or 0) + (resultado[1] or 0))) * 100,
            'detalhes_diarios': [
                {
                    'data': detalhe[0],
                    'enviados': detalhe[1],
                    'falhados': detalhe[2],
                    'recuperacao': detalhe[3],
                    'cadastro': detalhe[4]
                }
                for detalhe in detalhes_diarios
            ]
        }
    
    def obter_logs_recentes(self, limite: int = 50) -> List[Dict]:
        """Obtém os logs mais recentes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, tipo_email, destinatario, assunto, status, erro, 
                   tamanho_anexo, ip_origem, tempo_processamento_ms
            FROM email_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limite,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'tipo_email': row[1],
                'destinatario': row[2],
                'assunto': row[3],
                'status': row[4],
                'erro': row[5],
                'tamanho_anexo': row[6],
                'ip_origem': row[7],
                'tempo_processamento_ms': row[8]
            })
        
        conn.close()
        return logs
    
    def gerar_relatorio_completo(self) -> str:
        """Gera um relatório completo em texto"""
        estatisticas = self.obter_estatisticas_periodo(30)  # 30 dias
        logs_recentes = self.obter_logs_recentes(20)
        
        relatorio = f"""
📊 RELATÓRIO DE MONITORAMENTO DE EMAILS - FAD
═══════════════════════════════════════════════════════════
📅 Período: Últimos 30 dias
🕐 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📈 ESTATÍSTICAS GERAIS:
──────────────────────────────────────────────────────────
✅ Total de emails enviados: {estatisticas['total_enviados']}
❌ Total de falhas: {estatisticas['total_falhados']}
📊 Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%
⏱️  Tempo médio de processamento: {estatisticas['tempo_medio_ms']:.0f}ms
📧 Dias com atividade: {estatisticas['dias_com_atividade']}

📋 BREAKDOWN POR TIPO:
──────────────────────────────────────────────────────────
🔐 Emails de recuperação de senha: {estatisticas['emails_recuperacao']}
👥 Emails de confirmação de cadastro: {estatisticas['emails_cadastro']}

📅 ATIVIDADE DIÁRIA (últimos 7 dias):
──────────────────────────────────────────────────────────"""

        for detalhe in estatisticas['detalhes_diarios'][:7]:
            relatorio += f"""
{detalhe['data']}: {detalhe['enviados']} enviados, {detalhe['falhados']} falhas"""

        relatorio += f"""

🕐 LOGS RECENTES (últimos 20):
──────────────────────────────────────────────────────────"""

        for log in logs_recentes:
            status_emoji = "✅" if log['status'] == 'sucesso' else "❌"
            tipo_emoji = "🔐" if log['tipo_email'] == 'recuperacao_senha' else "👥"
            relatorio += f"""
{log['timestamp']} | {status_emoji} {tipo_emoji} | {log['destinatario']} | {log['status']}"""
            if log['erro']:
                relatorio += f" | ERRO: {log['erro']}"

        relatorio += f"""

════════════════════════════════════════════════════════════
📁 Logs detalhados salvos em: {self.db_path}
🔄 Para atualizar este relatório, execute: python monitorar_emails.py
════════════════════════════════════════════════════════════
"""
        return relatorio
    
    def exportar_logs_json(self, dias: int = 30) -> str:
        """Exporta logs para JSON"""
        data_inicio = datetime.now() - timedelta(days=dias)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM email_logs 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (data_inicio,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'timestamp': row[1],
                'tipo_email': row[2],
                'destinatario': row[3],
                'remetente': row[4],
                'assunto': row[5],
                'status': row[6],
                'erro': row[7],
                'tamanho_anexo': row[8],
                'ip_origem': row[9],
                'user_agent': row[10],
                'tempo_processamento_ms': row[11]
            })
        
        conn.close()
        
        arquivo_json = self.log_dir / f"email_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump({
                'periodo_dias': dias,
                'data_exportacao': datetime.now().isoformat(),
                'total_logs': len(logs),
                'logs': logs
            }, f, indent=2, ensure_ascii=False)
        
        return str(arquivo_json)
    
    def gerar_relatorio(self) -> dict:
        """Gera relatório básico como dicionário para compatibilidade"""
        estatisticas = self.obter_estatisticas_periodo(30)
        return {
            'total_envios': estatisticas['total_enviados'],
            'total_falhados': estatisticas['total_falhados'],
            'taxa_sucesso': estatisticas['taxa_sucesso'],
            'emails_recuperacao': estatisticas['emails_recuperacao'],
            'emails_cadastro': estatisticas['emails_cadastro'],
            'tempo_medio_ms': estatisticas['tempo_medio_ms']
        }

# Instância global do monitor
email_monitor = EmailLogMonitor()

def main():
    """Função principal para execução do script"""
    print("📊 SISTEMA DE MONITORAMENTO DE EMAILS FAD")
    print("=" * 60)
    
    monitor = EmailLogMonitor()
    
    # Gera relatório completo
    relatorio = monitor.gerar_relatorio_completo()
    print(relatorio)
    
    # Salva relatório em arquivo
    arquivo_relatorio = monitor.log_dir / f"relatorio_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print(f"\n📄 Relatório salvo em: {arquivo_relatorio}")
    
    # Exporta logs em JSON
    arquivo_json = monitor.exportar_logs_json()
    print(f"📋 Logs exportados em JSON: {arquivo_json}")

if __name__ == "__main__":
    main()
