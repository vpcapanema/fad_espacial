# ========================================================================
# 📁 BACKUP DE CONFIGURAÇÃO DE ROTAS VALIDADAS - FAD
# ========================================================================
# Data: 17/06/2025
# Sistema: Ferramenta de Análise Dinamizada (FAD)
# Responsável: Sistema de Auditoria FAD
# 
# Este arquivo contém o backup das rotas validadas e funcionais.
# Use este arquivo para restaurar as configurações em caso de problemas.
# ========================================================================

# 🔐 ROTAS CRÍTICAS VALIDADAS - 17/06/2025

ROTAS_VALIDADAS = {
    "autenticacao": {
        "router": "autenticacao_router",
        "prefix": None,
        "status": "VALIDADO",
        "data": "17/06/2025",
        "criticidade": "ALTA",
        "descricao": "Sistema de login e autenticação"
    },
    
    "painel_master": {
        "router": "painel_master_router",
        "prefix": "/painel-master",
        "status": "VALIDADO",
        "data": "17/06/2025",
        "criticidade": "CRÍTICA",
        "descricao": "Painel principal do sistema - funcionalidades master"
    },
    
    "auditoria_exportacao": {
        "router": "auditoria_exportacao_router",
        "prefix": "/painel-master",
        "status": "VALIDADO",
        "data": "17/06/2025",
        "criticidade": "CRÍTICA",
        "descricao": "Sistema de auditoria e exportação de dados - RECÉM IMPLEMENTADO"
    },
    
    "painel_coordenador": {
        "router": "painel_administrador_router",
        "prefix": "/painel-coordenador",
        "status": "VALIDADO",
        "data": "17/06/2025",
        "criticidade": "ALTA",
        "descricao": "Painel do coordenador/administrador"
    },
    
    "painel_analista": {
        "router": "painel_usuario_comum_router",
        "prefix": "/painel-analista",
        "status": "VALIDADO",
        "data": "17/06/2025",
        "criticidade": "ALTA",
        "descricao": "Painel do analista/usuário comum"
    }
}

# 📋 ENDPOINTS ESPECÍFICOS VALIDADOS

ENDPOINTS_CRITICOS = [
    "GET /painel-master/",
    "GET /painel-master/dados/analistas",
    "GET /painel-master/dados/coordenadores", 
    "GET /painel-master/dados/todos-usuarios",
    "GET /painel-master/auditoria/pessoa-fisica/{id}",
    "GET /painel-master/auditoria/pessoa-juridica/{id}",
    "GET /painel-master/exportar/pessoa-fisica/{id}/{formato}",
    "GET /painel-master/exportar/pessoa-juridica/{id}/{formato}",
    "POST /painel-master/acao/aprovar-usuario/{id}",
    "POST /painel-master/acao/reprovar-usuario/{id}",
    "POST /painel-master/acao/ativar-usuario/{id}",
    "POST /painel-master/acao/desativar-usuario/{id}"
]

# 🔧 CONFIGURAÇÕES DE PROTEÇÃO

PROTECAO_CONFIG = {
    "backup_automatico": True,
    "validacao_obrigatoria": True,
    "log_alteracoes": True,
    "notificacao_admin": True,
    "rollback_automatico": False
}

# 📝 INSTRUÇÕES DE RESTAURAÇÃO

INSTRUCOES_RESTAURACAO = """
Em caso de problemas com as rotas, siga estes passos:

1. BACKUP:
   - Faça backup do main.py atual antes de qualquer mudança

2. VERIFICAÇÃO:
   - Teste os endpoints críticos listados em ENDPOINTS_CRITICOS
   - Verifique se o servidor inicia sem erros

3. RESTAURAÇÃO:
   - Use as configurações em ROTAS_VALIDADAS para restaurar
   - Mantenha os prefixes exatamente como especificado
   - Respeite a ordem de inclusão das rotas

4. VALIDAÇÃO:
   - Teste login/logout
   - Teste painéis (master, coordenador, analista)
   - Teste sistema de auditoria e exportação
   - Verifique PostgreSQL conectado

5. CONTATO:
   - Em caso de dúvidas, consulte este arquivo
   - Mantenha log de todas as alterações
"""

# ⚠️  AVISOS IMPORTANTES

AVISOS = [
    "NUNCA alterar prefixes das rotas validadas",
    "SEMPRE testar em ambiente de desenvolvimento primeiro", 
    "MANTER ordem de inclusão das rotas",
    "BACKUP obrigatório antes de qualquer mudança",
    "Sistema de auditoria é CRÍTICO - não modificar",
    "PostgreSQL deve estar sempre conectado",
    "Sessões de usuário são controladas por middleware"
]

# 🔍 ÚLTIMA VALIDAÇÃO
ULTIMA_VALIDACAO = {
    "data": "17/06/2025",
    "hora": "12:45:00",
    "servidor": "FUNCIONANDO",
    "postgresql": "CONECTADO",
    "rotas_testadas": len(ENDPOINTS_CRITICOS),
    "status_geral": "✅ TODAS AS ROTAS FUNCIONAIS"
}
