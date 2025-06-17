#!/bin/bash
# 🔐 SCRIPT DE PROTEÇÃO DE ROTAS - FAD
# ===================================
# Execute este script antes de qualquer modificação no main.py

echo "🔐 SISTEMA DE PROTEÇÃO DE ROTAS - FAD"
echo "====================================="

# Criar backup automático do main.py
BACKUP_FILE="main.py.backup.$(date +%Y%m%d_%H%M%S)"
echo "📁 Criando backup: $BACKUP_FILE"
cp main.py "$BACKUP_FILE"

# Executar validação das rotas
echo "🔍 Validando rotas críticas..."
python validar_rotas_criticas.py

if [ $? -eq 0 ]; then
    echo "✅ Todas as rotas críticas estão funcionando!"
    echo "✅ Backup criado com sucesso: $BACKUP_FILE"
    echo ""
    echo "⚠️  LEMBRE-SE:"
    echo "   - NÃO altere rotas marcadas como CRÍTICO"
    echo "   - SEMPRE teste após modificações"
    echo "   - Execute 'python validar_rotas_criticas.py' após mudanças"
    echo ""
    echo "🚀 Sistema pronto para modificações!"
else
    echo "❌ PROBLEMAS DETECTADOS nas rotas críticas!"
    echo "❌ NÃO faça modificações até resolver os problemas"
    echo "📄 Consulte: relatorio_validacao_rotas.json"
    exit 1
fi
