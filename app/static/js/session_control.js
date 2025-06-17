/**
 * 🔐 FAD Session Control - Frontend
 * Sistema avançado de controle de sessão no frontend
 */

class FADSessionController {
    constructor(options = {}) {
        // ⚙️ Configurações
        this.config = {
            apiBase: '/api/session',
            autoRenewEnabled: true,
            autoRenewThreshold: 180, // 3 minutos em segundos
            activityEvents: ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'],
            warningThreshold: 300,   // 5 minutos
            criticalThreshold: 120,  // 2 minutos
            renewalCooldown: 30000,  // 30 segundos entre auto-renovações
            ...options
        };
        
        // 🔄 Estado interno
        this.timeLeft = 54000;
        this.status = 'unknown';
        this.isActive = true;
        this.lastActivity = Date.now();
        this.lastAutoRenewal = 0;
        this.warningShown = false;
        this.criticalWarningShown = false;
        
        // 🎨 Elementos DOM
        this.timerElement = null;
        this.statusElement = null;
        
        // ⚡ Inicialização
        this.init();
    }
    
    /**
     * 🚀 Inicializa o sistema de controle de sessão
     */
    init() {
        this.findDOMElements();
        this.setupActivityTracking();
        this.startStatusPolling();
        this.setupEventListeners();
        
        console.log('🔐 FAD Session Controller inicializado');
    }
    
    /**
     * 🔍 Encontra elementos DOM necessários
     */
    findDOMElements() {
        this.timerElement = document.getElementById('session-timer');
        this.statusElement = document.getElementById('session-status');
        
        if (!this.timerElement) {
            console.warn('⚠️ Elemento session-timer não encontrado');
        }
    }
    
    /**
     * 👆 Configura rastreamento de atividade do usuário
     */
    setupActivityTracking() {
        this.config.activityEvents.forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivity = Date.now();
                this.isActive = true;
            }, { passive: true });
        });
        
        // Detectar inatividade
        setInterval(() => {
            const inactive = (Date.now() - this.lastActivity) > 60000; // 1 minuto
            if (inactive !== !this.isActive) {
                this.isActive = !inactive;
                console.log(`👤 Usuário ${this.isActive ? 'ativo' : 'inativo'}`);
            }
        }, 5000);
    }
    
    /**
     * 📡 Inicia polling de status da sessão
     */
    startStatusPolling() {
        this.checkSessionStatus();
        
        // Verificar status a cada 30 segundos
        setInterval(() => {
            this.checkSessionStatus();
        }, 30000);
        
        // Timer visual a cada segundo
        setInterval(() => {
            this.updateTimer();
        }, 1000);
    }
    
    /**
     * 🔍 Verifica status atual da sessão
     */
    async checkSessionStatus() {
        try {
            const response = await fetch(`${this.config.apiBase}/status`);
            const data = await response.json();
            
            if (!data.authenticated) {
                this.handleSessionExpired();
                return;
            }
            
            this.timeLeft = data.remaining_seconds;
            this.status = data.status;
            
            // Auto-renovação se necessário
            if (this.shouldAutoRenew(data)) {
                await this.autoRenewSession();
            }
            
            // Avisos visuais
            this.handleWarnings();
            
        } catch (error) {
            console.error('❌ Erro ao verificar status da sessão:', error);
            this.showError('Erro de conexão com o servidor');
        }
    }
    
    /**
     * 🔄 Verifica se deve renovar automaticamente
     */
    shouldAutoRenew(sessionData) {
        if (!this.config.autoRenewEnabled) return false;
        if (!this.isActive) return false;
        if (!sessionData.can_renew) return false;
        if (sessionData.remaining_seconds > this.config.autoRenewThreshold) return false;
        
        // Cooldown entre renovações
        const now = Date.now();
        if ((now - this.lastAutoRenewal) < this.config.renewalCooldown) return false;
        
        return true;
    }
    
    /**
     * ⚡ Renovação automática da sessão
     */
    async autoRenewSession() {
        try {
            const response = await fetch(`${this.config.apiBase}/auto-renew`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.lastAutoRenewal = Date.now();
                this.timeLeft = result.new_timeout_seconds;
                this.resetWarnings();
                
                this.showSuccess('🔄 Sessão renovada automaticamente');
                console.log('✅ Sessão auto-renovada:', result.message);
            }
            
        } catch (error) {
            console.error('❌ Erro na auto-renovação:', error);
        }
    }
    
    /**
     * 🔄 Renovação manual da sessão
     */
    async renewSession() {
        try {
            const response = await fetch(`${this.config.apiBase}/renew`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.timeLeft = result.new_timeout_seconds;
                this.resetWarnings();
                this.showSuccess(`✅ ${result.message}`);
            } else {
                this.showError(`❌ ${result.message}`);
            }
            
        } catch (error) {
            console.error('❌ Erro ao renovar sessão:', error);
            this.showError('Erro ao renovar sessão');
        }
    }
    
    /**
     * ⏱️ Atualiza o timer visual
     */
    updateTimer() {
        if (this.timeLeft <= 0) {
            this.handleSessionExpired();
            return;
        }
        
        this.timeLeft--;
        
        if (this.timerElement) {
            this.timerElement.textContent = this.formatTime(this.timeLeft);
            this.timerElement.style.color = this.getTimerColor();
        }
        
        this.handleWarnings();
    }
    
    /**
     * 🎨 Formatação do tempo para display
     */
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    /**
     * 🎨 Cor do timer baseada no tempo restante
     */
    getTimerColor() {
        if (this.timeLeft <= this.config.criticalThreshold) return '#ff0000';
        if (this.timeLeft <= this.config.warningThreshold) return '#ff9800';
        return '#d32f2f';
    }
    
    /**
     * ⚠️ Gerencia avisos visuais
     */
    handleWarnings() {
        // Aviso crítico (2 minutos)
        if (this.timeLeft <= this.config.criticalThreshold && !this.criticalWarningShown) {
            this.criticalWarningShown = true;
            this.showCriticalWarning();
        }
        
        // Aviso normal (5 minutos)
        else if (this.timeLeft <= this.config.warningThreshold && !this.warningShown) {
            this.warningShown = true;
            this.showWarning();
        }
    }
    
    /**
     * ⚠️ Exibe aviso normal
     */
    showWarning() {
        const minutes = Math.ceil(this.timeLeft / 60);
        this.showToast(`⚠️ Sua sessão expira em ${minutes} minutos`, 'warning', 8000);
        
        // Oferecer renovação
        if (this.timeLeft <= this.config.autoRenewThreshold) {
            this.showRenewDialog();
        }
    }
    
    /**
     * 🚨 Exibe aviso crítico
     */
    showCriticalWarning() {
        const seconds = this.timeLeft;
        this.showToast(`🚨 ATENÇÃO: Sessão expira em ${seconds} segundos!`, 'error', 10000);
        
        // Mostrar dialog de renovação obrigatória
        this.showRenewDialog(true);
    }
    
    /**
     * 💬 Exibe dialog de renovação
     */
    showRenewDialog(critical = false) {
        const message = critical 
            ? '🚨 Sua sessão está prestes a expirar!\n\nClique em OK para renovar ou será desconectado automaticamente.'
            : '⚠️ Sua sessão expirará em breve.\n\nDeseja renovar por mais 15 minutos?';
        
        if (confirm(message)) {
            this.renewSession();
        }
    }
    
    /**
     * ❌ Manipula expiração da sessão
     */
    handleSessionExpired() {
        this.showToast('🔒 Sua sessão expirou! Redirecionando para o login...', 'error', 5000);
        
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    }
    
    /**
     * 🔄 Reseta avisos mostrados
     */
    resetWarnings() {
        this.warningShown = false;
        this.criticalWarningShown = false;
    }
    
    /**
     * 🎯 Configura event listeners
     */
    setupEventListeners() {
        // Botão de renovação manual (se existir)
        const renewBtn = document.getElementById('renew-session-btn');
        if (renewBtn) {
            renewBtn.addEventListener('click', () => this.renewSession());
        }
        
        // Detecção de foco/blur da janela
        window.addEventListener('focus', () => {
            this.checkSessionStatus(); // Verificar ao voltar à aba
        });
        
        // Antes de sair da página
        window.addEventListener('beforeunload', (event) => {
            if (this.timeLeft > 0 && this.timeLeft < 300) {
                event.preventDefault();
                event.returnValue = 'Você tem uma sessão ativa que expirará em breve. Tem certeza que deseja sair?';
            }
        });
    }
    
    /**
     * 📢 Sistema de notificações toast
     */
    showToast(message, type = 'info', duration = 5000) {
        // Remover toasts existentes do mesmo tipo
        const existingToasts = document.querySelectorAll(`.fad-toast.${type}`);
        existingToasts.forEach(toast => toast.remove());
        
        // Criar novo toast
        const toast = document.createElement('div');
        toast.className = `fad-toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;
        
        // Adicionar estilos se não existirem
        this.addToastStyles();
        
        // Adicionar ao DOM
        document.body.appendChild(toast);
        
        // Auto-remover
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
    }
    
    /**
     * ✅ Notificação de sucesso
     */
    showSuccess(message) {
        this.showToast(message, 'success', 3000);
    }
    
    /**
     * ❌ Notificação de erro
     */
    showError(message) {
        this.showToast(message, 'error', 5000);
    }
    
    /**
     * 🎨 Adiciona estilos para toasts
     */
    addToastStyles() {
        if (document.getElementById('fad-toast-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'fad-toast-styles';
        styles.textContent = `
            .fad-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                animation: slideInRight 0.3s ease;
            }
            
            .fad-toast.success { border-left: 4px solid #4caf50; }
            .fad-toast.warning { border-left: 4px solid #ff9800; }
            .fad-toast.error { border-left: 4px solid #f44336; }
            .fad-toast.info { border-left: 4px solid #2196f3; }
            
            .toast-content {
                display: flex;
                align-items: center;
                padding: 12px 16px;
            }
            
            .toast-message {
                flex: 1;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .toast-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #666;
                margin-left: 12px;
            }
            
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    /**
     * 📊 Obter estatísticas da sessão
     */
    getSessionInfo() {
        return {
            timeLeft: this.timeLeft,
            status: this.status,
            isActive: this.isActive,
            lastActivity: this.lastActivity,
            warningShown: this.warningShown,
            criticalWarningShown: this.criticalWarningShown
        };
    }
}

// 🚀 Auto-inicialização quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se há sessão ativa
    const sessionTimer = document.getElementById('session-timer');
    if (sessionTimer) {
        // Inicializar controlador de sessão
        window.fadSessionController = new FADSessionController();
        
        console.log('✅ Sistema de controle de sessão FAD ativo');
    }
});

// 🔧 Funções globais para uso em templates
window.FADSession = {
    renew: () => window.fadSessionController?.renewSession(),
    getInfo: () => window.fadSessionController?.getSessionInfo(),
    showStatus: () => console.log(window.fadSessionController?.getSessionInfo())
};
