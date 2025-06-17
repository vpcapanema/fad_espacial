# Script PowerShell para adicionar o psql ao PATH do Windows e testar no VS Code
# 1. Defina o caminho do binário do PostgreSQL (ajuste a versão se necessário)
$pgsqlBin = "C:\Program Files\PostgreSQL\15\bin"

# 2. Adiciona ao PATH do usuário, se ainda não estiver
if ($env:PATH -notlike "*$pgsqlBin*") {
    [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";" + $pgsqlBin, [EnvironmentVariableTarget]::User)
    Write-Host "Caminho do PostgreSQL adicionado ao PATH do usuário."
} else {
    Write-Host "Caminho do PostgreSQL já está no PATH."
}

# 3. Testa se o psql está disponível
$psqlTest = & psql --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "psql disponível no terminal!"
    Write-Host "Para usar, abra um novo terminal no VS Code e execute:"
    Write-Host "psql -U postgres -d fad_db"
} else {
    Write-Host "psql NÃO encontrado. Reinicie o VS Code e tente novamente."
}
