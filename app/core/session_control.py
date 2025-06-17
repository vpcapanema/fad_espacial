"""
🔐 FAD Session Control System
Controle avançado de sessão com melhorias de segurança e UX
"""

from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

class FADSessionManager:
    """Gerenciador central de sessões do sistema FAD"""
    
    # ⚙️ Configurações de tempo
    TIMEOUT_MINUTES = 15           # Tempo total da sessão
    WARNING_MINUTES = 5            # Quando mostrar primeiro aviso
    CRITICAL_MINUTES = 2           # Quando mostrar aviso crítico
    RENEWAL_THRESHOLD = 3          # Renovar automaticamente se restarem <= 3 min
    
    # 🔒 Configurações de segurança
    MAX_RENEWALS_PER_SESSION = 10  # Máximo de renovações por sessão
    ACTIVITY_THRESHOLD = 30        # Segundos mínimos entre renovações automáticas
    
    def __init__(self):
        self.active_sessions = {}  # Cache de sessões ativas
        
    def create_session(self, request: Request, user_data: dict) -> dict:
        """Cria uma nova sessão para o usuário"""
        now = datetime.utcnow().timestamp()
        
        session_data = {
            'usuario_id': user_data.get('id'),
            'usuario_nome': user_data.get('nome'),
            'usuario_email': user_data.get('email'),
            'usuario_tipo': user_data.get('tipo'),
            'created_at': now,
            'last_active': now,
            'renewals_count': 0,
            'last_renewal': now,
            'ip_address': request.client.host if request.client else 'unknown'
        }
        
        # Salvar na sessão do FastAPI
        for key, value in session_data.items():
            request.session[key] = value
            
        # Cache local para verificações rápidas
        session_id = request.session.get('session_id', f"sess_{now}")
        self.active_sessions[session_id] = session_data
        
        logger.info(f"Nova sessão criada para usuário {user_data.get('nome')} (ID: {user_data.get('id')})")
        
        return session_data
    
    def check_session_validity(self, request: Request) -> dict:
        logger.info(f"--- Checking session validity for path: {request.url.path} ---") # Log Adicionado
        if 'session' not in request.scope:
            logger.warning("No session in request.scope") # Log Adicionado
            return {'valid': False, 'reason': 'no_session', 'action': 'redirect_login'}

        session = request.session
        last_active = session.get('last_active')
        usuario_nome = session.get('usuario_nome', 'Unknown') # Log Adicionado

        logger.info(f"User: {usuario_nome}, Last active from session: {last_active}") # Log Adicionado

        if not last_active:
            logger.warning(f"User: {usuario_nome}, No last_active timestamp in session.") # Log Adicionado
            return {'valid': False, 'reason': 'no_timestamp', 'action': 'redirect_login'}

        now = datetime.utcnow().timestamp()
        elapsed = now - last_active
        remaining = (self.TIMEOUT_MINUTES * 60) - elapsed

        logger.info(f"User: {usuario_nome}, Now: {now}, Elapsed: {elapsed:.2f}s, Remaining: {remaining:.2f}s") # Log Adicionado

        if elapsed > self.TIMEOUT_MINUTES * 60:
            logger.warning(f"User: {usuario_nome}, Session expired. Elapsed: {elapsed:.2f}s") # Log Adicionado
            self.destroy_session(request)
            return {
                'valid': False, 
                'reason': 'expired', 
                'action': 'redirect_login',
                'elapsed_minutes': round(elapsed / 60, 1)
            }
        
        # Atualizar timestamp de atividade
        # logger.info(f"User: {usuario_nome}, Updating last_active from {session.get('last_active')} to {now}") # Log ANTES da atualização
        session['last_active'] = now
        # logger.info(f"User: {usuario_nome}, Updated last_active to {session.get('last_active')}") # Log DEPOIS da atualização
        
        # Determinar status da sessão
        remaining_minutes = remaining / 60
        
        if remaining_minutes <= self.CRITICAL_MINUTES:
            status = 'critical'
        elif remaining_minutes <= self.WARNING_MINUTES:
            status = 'warning'
        else:
            status = 'active'
        
        return {
            'valid': True,
            'status': status,
            'remaining_seconds': int(remaining),
            'remaining_minutes': round(remaining_minutes, 1),
            'can_renew': remaining_minutes <= self.RENEWAL_THRESHOLD,
            'renewals_count': session.get('renewals_count', 0),
            'usuario_nome': session.get('usuario_nome'),
            'usuario_tipo': session.get('usuario_tipo')
        }
    
    def renew_session(self, request: Request, auto_renewal: bool = False) -> dict:
        """Renova a sessão atual com validações de segurança"""
        session = request.session
        
        # Verificações de segurança
        renewals_count = session.get('renewals_count', 0)
        last_renewal = session.get('last_renewal', 0)
        now = datetime.utcnow().timestamp()
        
        # Limite de renovações
        if renewals_count >= self.MAX_RENEWALS_PER_SESSION:
            return {
                'success': False, 
                'reason': 'max_renewals_exceeded',
                'message': 'Limite de renovações excedido. Faça login novamente.'
            }
        
        # Throttling de renovações automáticas
        if auto_renewal and (now - last_renewal) < self.ACTIVITY_THRESHOLD:
            return {
                'success': False,
                'reason': 'too_frequent',
                'message': 'Aguarde antes de renovar novamente.'
            }
        
        # Renovar sessão
        session['last_active'] = now
        session['last_renewal'] = now
        session['renewals_count'] = renewals_count + 1
        
        new_timeout = self.TIMEOUT_MINUTES * 60
        
        logger.info(f"Sessão renovada para usuário {session.get('usuario_nome')} "
                   f"(Renovação #{renewals_count + 1})")
        
        return {
            'success': True,
            'new_timeout_seconds': new_timeout,
            'new_timeout_minutes': self.TIMEOUT_MINUTES,
            'renewals_count': renewals_count + 1,
            'message': f'Sessão renovada por mais {self.TIMEOUT_MINUTES} minutos'
        }
    
    def destroy_session(self, request: Request) -> None:
        """Destrói completamente a sessão"""
        session = request.session
        usuario_nome = session.get('usuario_nome', 'Usuário desconhecido')
        
        # Limpar cache local
        session_id = session.get('session_id')
        if session_id and session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Limpar sessão do FastAPI
        session.clear()
        
        logger.info(f"Sessão destruída para {usuario_nome}")
    
    def get_session_stats(self) -> dict:
        """Retorna estatísticas das sessões ativas"""
        active_count = len(self.active_sessions)
        
        if active_count == 0:
            return {'active_sessions': 0, 'users': []}
        
        users = []
        for session_data in self.active_sessions.values():
            users.append({
                'nome': session_data.get('usuario_nome'),
                'tipo': session_data.get('usuario_tipo'),
                'created_at': datetime.fromtimestamp(session_data.get('created_at', 0)).strftime('%H:%M:%S'),
                'renewals': session_data.get('renewals_count', 0)
            })
        
        return {
            'active_sessions': active_count,
            'users': users
        }

# Instância global do gerenciador de sessão
session_manager = FADSessionManager()

class FADSessionMiddleware(BaseHTTPMiddleware):
    """Middleware avançado de controle de sessão do FAD"""
    
    def __init__(self, app):
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next):
        # URLs que não precisam de verificação de sessão
        exempt_urls = [
            '/login', '/logout', '/static', '/favicon.ico',
            '/api/session/renew', '/api/session/status',
            '/debug', '/cabecalho-fad', '/mapa-rotas-fad'
        ]
        
        # Verificar se a URL precisa de autenticação
        needs_auth = not any(request.url.path.startswith(url) for url in exempt_urls)
        
        if needs_auth and 'session' in request.scope:
            session_status = session_manager.check_session_validity(request)
            
            if not session_status['valid']:
                # Sessão inválida - redirecionar para login
                response = RedirectResponse(url="/login")
                response.delete_cookie('session')
                return response
            
            # Adicionar dados da sessão ao request para templates
            request.state.session_data = session_status
        
        response = await call_next(request)
        return response

# Função helper para templates
def get_session_context(request: Request) -> dict:
    """Retorna contexto de sessão para templates"""
    if not hasattr(request.state, 'session_data'):
        return {}
    
    session_data = request.state.session_data
    
    return {
        'usuario': {
            'nome': request.session.get('usuario_nome', ''),
            'email': request.session.get('usuario_email', ''),
            'tipo': request.session.get('usuario_tipo', ''),
            'id': request.session.get('usuario_id', '')
        },
        'tempo_restante': session_data.get('remaining_seconds', 0),
        'session_status': session_data.get('status', 'unknown'),
        'can_renew': session_data.get('can_renew', False),
        'renewals_count': session_data.get('renewals_count', 0)
    }

# Endpoints de API para controle de sessão
from fastapi import APIRouter

session_router = APIRouter(prefix="/api/session", tags=["Session Management"])

@session_router.get("/status")
async def get_session_status(request: Request):
    """Retorna status atual da sessão"""
    if 'session' not in request.scope:
        return JSONResponse({"authenticated": False})
    
    status = session_manager.check_session_validity(request)
    return JSONResponse({
        "authenticated": status['valid'],
        "status": status.get('status', 'unknown'),
        "remaining_seconds": status.get('remaining_seconds', 0),
        "remaining_minutes": status.get('remaining_minutes', 0),
        "can_renew": status.get('can_renew', False),
        "renewals_count": status.get('renewals_count', 0)
    })

@session_router.post("/renew")
async def renew_session(request: Request):
    """Renova a sessão atual"""
    if 'session' not in request.scope:
        return JSONResponse({"success": False, "reason": "no_session"}, status_code=401)
    
    result = session_manager.renew_session(request)
    status_code = 200 if result['success'] else 400
    
    return JSONResponse(result, status_code=status_code)

@session_router.post("/auto-renew")
async def auto_renew_session(request: Request):
    """Renovação automática baseada em atividade"""
    if 'session' not in request.scope:
        return JSONResponse({"success": False, "reason": "no_session"}, status_code=401)
    
    result = session_manager.renew_session(request, auto_renewal=True)
    status_code = 200 if result['success'] else 400
    
    return JSONResponse(result, status_code=status_code)

@session_router.get("/stats")
async def get_session_stats(request: Request):
    """Estatísticas de sessões ativas (apenas para admins)"""
    # Verificar se é admin/master
    user_type = request.session.get('usuario_tipo', '')
    if user_type not in ['master', 'coordenador']:
        return JSONResponse({"error": "Acesso negado"}, status_code=403)
    
    stats = session_manager.get_session_stats()
    return JSONResponse(stats)

@session_router.post("/logout")
async def logout(request: Request):
    """Logout completo da sessão"""
    session_manager.destroy_session(request)
    response = JSONResponse({"success": True, "message": "Logout realizado com sucesso"})
    response.delete_cookie('session')
    return response
