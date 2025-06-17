# 🔐 SCRIPT DE PROTEÇÃO DE ROTAS - FAD (PowerShell)
# ================================================
# Execute este script antes de qualquer modificação no main.py

Write-Host "🔐 SISTEMA DE PROTEÇÃO DE ROTAS - FAD" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Criar backup automático do main.py
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "main.py.backup.$timestamp"

Write-Host "📁 Criando backup: $backupFile" -ForegroundColor Yellow
Copy-Item "main.py" $backupFile

# Executar validação das rotas
Write-Host "🔍 Validando rotas críticas..." -ForegroundColor Yellow
$result = python validar_rotas_criticas.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Todas as rotas críticas estão funcionando!" -ForegroundColor Green
    Write-Host "✅ Backup criado com sucesso: $backupFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  LEMBRE-SE:" -ForegroundColor Yellow
    Write-Host "   - NÃO altere rotas marcadas como CRÍTICO" -ForegroundColor Red
    Write-Host "   - SEMPRE teste após modificações" -ForegroundColor Red
    Write-Host "   - Execute 'python validar_rotas_criticas.py' após mudanças" -ForegroundColor Red
    Write-Host ""
    Write-Host "🚀 Sistema pronto para modificações!" -ForegroundColor Green
} else {
    Write-Host "❌ PROBLEMAS DETECTADOS nas rotas críticas!" -ForegroundColor Red
    Write-Host "❌ NÃO faça modificações até resolver os problemas" -ForegroundColor Red
    Write-Host "📄 Consulte: relatorio_validacao_rotas.json" -ForegroundColor Yellow
    exit 1
}

# Pausa para o usuário ler as mensagens
Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
