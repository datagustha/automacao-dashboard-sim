/**
 * APP - Lógica Principal
 * =======================
 */

// ================================================================
// CONFIGURAÇÃO
// ================================================================

const CONFIG = {
    API_BASE: '/api',
};

let dadosCompletos = {};
let operadorLogado = null;

// ================================================================
// INICIALIZAÇÃO
// ================================================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Dashboard V2 - Operador');
    
    // Verifica sessão
    const sessionData = await verificarSessao();
    if (!sessionData) {
        window.location.href = '/login';
        return;
    }
    
    operadorLogado = sessionData;
    atualizarUsuario(operadorLogado);
    
    // Configura mês e ano atual
    const mesAtual = getMesAtual();
    const anoAtual = getAnoAtual();
    
    const filtroMes = document.getElementById('filtro-mes');
    const filtroAno = document.getElementById('filtro-ano');
    
    if (filtroMes) filtroMes.value = mesAtual;
    if (filtroAno) filtroAno.value = anoAtual;
    
    // Atualiza data
    document.getElementById('currentDate').textContent = getDataAtual();
    
    // Carrega dados
    await carregarDados();
    
    // Configura eventos
    if (filtroMes) filtroMes.addEventListener('change', carregarDados);
    if (filtroAno) filtroAno.addEventListener('change', carregarDados);
    
    // Configura logout
    const logoutBtn = document.querySelector('.btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});

// ================================================================
// SESSÃO
// ================================================================

async function verificarSessao() {
    try {
        const response = await fetch('/api/session');
        const data = await response.json();
        if (data.success) {
            return data.data;
        }
        return null;
    } catch (error) {
        console.error('Erro ao verificar sessão:', error);
        return null;
    }
}

// ================================================================
// CARREGAR DADOS
// ================================================================

async function carregarDados() {
    try {
        const login = operadorLogado ? operadorLogado.login : null;
        if (!login) {
            console.warn('⚠️ Nenhum operador logado');
            return;
        }
        
        const mes = document.getElementById('filtro-mes')?.value || getMesAtual();
        const ano = document.getElementById('filtro-ano')?.value || getAnoAtual();
        
        showLoading();
        
        const response = await fetch(`${CONFIG.API_BASE}/resumo/${login}?mes=${mes}&ano=${ano}`);
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            dadosCompletos = data.data;
            renderizarDashboard(data.data);
            
            // Atualiza pagamentos completos
            if (data.data.ultimos_pagamentos) {
                renderizarPagamentosCompletos(data.data.ultimos_pagamentos);
            }
        } else {
            console.error('Erro ao carregar dados:', data.message);
            showError('Erro ao carregar dados: ' + data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('Erro:', error);
        showError('Erro de conexão com o servidor');
    }
}

// ================================================================
// USUÁRIO
// ================================================================

function atualizarUsuario(operador) {
    if (!operador) return;
    
    const nome = operador.nome || 'Usuário';
    const primeiroNome = nome.split(' ')[0];
    document.getElementById('userName').textContent = nome;
    document.getElementById('userRole').textContent = operador.banco || 'Operador';
    
    // Saudação personalizada no header
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) {
        pageTitle.textContent = `Olá, ${primeiroNome}!`;
    }
    
    const avatarText = document.getElementById('userAvatarText');
    const avatarImg = document.getElementById('userAvatarImg');
    const imagemUrl = operador.imagem || null;
    const iniciais = getIniciais(nome);
    
    if (imagemUrl && avatarImg) {
        avatarImg.src = imagemUrl;
        avatarImg.style.display = 'block';
        if (avatarText) avatarText.style.display = 'none';
    } else if (avatarText) {
        avatarText.textContent = iniciais;
        avatarText.style.display = 'flex';
        if (avatarImg) avatarImg.style.display = 'none';
    }
}

// ================================================================
// NAVEGAÇÃO
// ================================================================

function navegar(pagina) {
    // Esconde todas as páginas
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // Mostra a página selecionada
    const pageElement = document.getElementById(`page-${pagina}`);
    if (pageElement) pageElement.classList.add('active');
    
    // Atualiza menu
    document.querySelectorAll('.sidebar-nav li').forEach(li => li.classList.remove('active'));
    const menuItem = document.querySelector(`.sidebar-nav li[data-page="${pagina}"]`);
    if (menuItem) menuItem.classList.add('active');
    
    // Atualiza título
    const titulos = {
        dashboard: 'Dashboard',
        pagamentos: 'Pagamentos',
        clientes: 'Clientes',
        performance: 'Performance',
        metas: 'Metas'
    };
    document.getElementById('pageTitle').textContent = titulos[pagina] || pagina;
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ================================================================
// FILTROS
// ================================================================

function filtrarDados() {
    carregarDados();
}

// ================================================================
// LOADING / ERROR
// ================================================================

function showLoading() {
    // Mostra indicador de carregamento
    const elementos = document.querySelectorAll('.chart-placeholder, .table-wrapper tbody');
    elementos.forEach(el => {
        if (!el.dataset.original) {
            el.dataset.original = el.innerHTML;
        }
        el.innerHTML = `
            <div style="text-align:center;padding:20px;color:#6B7280;">
                <i class="fas fa-spinner fa-spin" style="font-size:24px;"></i>
                <p style="margin-top:8px;">Carregando...</p>
            </div>
        `;
    });
}

function hideLoading() {
    // Restaura os elementos
    const elementos = document.querySelectorAll('.chart-placeholder, .table-wrapper tbody');
    elementos.forEach(el => {
        if (el.dataset.original) {
            el.innerHTML = el.dataset.original;
            delete el.dataset.original;
        }
    });
}

function showError(mensagem) {
    // Mostra toast de erro
    console.error('❌', mensagem);
    // Implementar toast visual aqui
}

// ================================================================
// LOGOUT
// ================================================================

async function logout() {
    if (!confirm('Deseja realmente sair?')) return;
    
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
        window.location.href = '/login';
    }
}

// ================================================================
// EXPORT
// ================================================================

// Funções globais para uso no HTML
window.navegar = navegar;
window.toggleSidebar = toggleSidebar;
window.filtrarDados = filtrarDados;
window.filtrarPagamentos = filtrarPagamentos;
window.logout = logout;