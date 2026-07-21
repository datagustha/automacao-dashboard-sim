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

window.dadosCompletos = {};
window.operadorLogado = null;
let dadosCompletos = window.dadosCompletos;
let operadorLogado = window.operadorLogado;

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
    
    window.operadorLogado = sessionData;
    operadorLogado = window.operadorLogado;
    atualizarUsuario(operadorLogado);

    // Exibe o multiselect de faixas se o operador for SEMEAR
    const multiselectFaixaContainerOp = document.getElementById('multiselect-faixa-op-container');
    if (multiselectFaixaContainerOp && operadorLogado?.banco === 'SEMEAR') {
        multiselectFaixaContainerOp.style.display = 'block';
    }
    
    // Configura mês e ano atual
    const mesAtual = getMesAtual();
    const anoAtual = getAnoAtual();
    
    const filtroMes = document.getElementById('filtro-mes');
    const filtroAno = document.getElementById('filtro-ano');
    
    if (filtroMes) filtroMes.value = mesAtual;
    if (filtroAno) filtroAno.value = anoAtual;
    
    // Inicializa filtros da página de pagamentos com o mês/ano atual
    const filtroPagMes = document.getElementById('filtro-pagamento-mes');
    const filtroPagAno = document.getElementById('filtro-pagamento-ano');
    if (filtroPagMes) filtroPagMes.value = mesAtual;
    if (filtroPagAno) filtroPagAno.value = anoAtual;
    
    // Atualiza data
    document.getElementById('currentDate').textContent = getDataAtual();
    
    // Carrega dados
    await carregarDados();

    // Badge do sidebar "Pagamentos" = sempre a quantidade do mês ATUAL real,
    // independente do filtro selecionado pelo usuário no dashboard (item 7).
    atualizarBadgePagamentosMesAtual();

    // Auto-atualização a cada 10 minutos para capturar novos pagamentos
    setInterval(() => {
        carregarDados();
        atualizarBadgePagamentosMesAtual();
    }, 600000);

    // Configura eventos
    // Mantém os dois pares de filtro de mês/ano (dashboard principal e aba
    // de Pagamentos) sempre sincronizados nos dois sentidos, pra evitar
    // filtrar com um mês na tela e outro "por trás" (bug que fazia
    // aparecer pagamento de mês errado).
    if (filtroMes) filtroMes.addEventListener('change', () => {
        if (filtroPagMes) filtroPagMes.value = filtroMes.value;
        const opPerfMes = document.getElementById('op-perf-mes');
        if (opPerfMes) opPerfMes.value = filtroMes.value;
        carregarDados();
    });
    if (filtroAno) filtroAno.addEventListener('change', () => {
        if (filtroPagAno) filtroPagAno.value = filtroAno.value;
        const opPerfAno = document.getElementById('op-perf-ano');
        if (opPerfAno) opPerfAno.value = filtroAno.value;
        carregarDados();
    });

    const opPerfMes = document.getElementById('op-perf-mes');
    if (opPerfMes) opPerfMes.addEventListener('change', () => {
        if (filtroMes) filtroMes.value = opPerfMes.value;
        if (filtroPagMes) filtroPagMes.value = opPerfMes.value;
        carregarDados();
    });

    const opPerfAno = document.getElementById('op-perf-ano');
    if (opPerfAno) opPerfAno.addEventListener('change', () => {
        if (filtroAno) filtroAno.value = opPerfAno.value;
        if (filtroPagAno) filtroPagAno.value = opPerfAno.value;
        carregarDados();
    });
    
    // Configura logout
    const logoutBtn = document.querySelector('.btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    // Inicialização do relógio e dados de ponto/horários
    if (typeof inicializarRelogioPonto === 'function') {
        inicializarRelogioPonto();
    }
    if (typeof renderizarPontoOperador === 'function') {
        renderizarPontoOperador();
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
// BADGE "PAGAMENTOS" DO SIDEBAR — SEMPRE O MÊS ATUAL REAL
// ================================================================
// Independente do filtro de mês/ano que o usuário está navegando no
// dashboard, esse número sempre representa a quantidade de pagamentos
// do mês corrente de verdade (hoje), por isso busca separado.

async function atualizarBadgePagamentosMesAtual() {
    try {
        const login = operadorLogado ? operadorLogado.login : null;
        if (!login) return;

        const mesAtualReal = getMesAtual();
        const anoAtualReal = getAnoAtual();

        const response = await fetch(`${CONFIG.API_BASE}/resumo/${login}?mes=${mesAtualReal}&ano=${anoAtualReal}`);
        const data = await response.json();

        const badgePagamentos = document.getElementById('badgePagamentos');
        if (badgePagamentos && data.success) {
            const totalMesAtual = (data.data.indicadores && data.data.indicadores.total_pagamentos) || 0;
            badgePagamentos.textContent = totalMesAtual;
        }
    } catch (error) {
        console.error('Erro ao atualizar badge de pagamentos do mês atual:', error);
    }
}
window.atualizarBadgePagamentosMesAtual = atualizarBadgePagamentosMesAtual;

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
            window.dadosCompletos = data.data;
            dadosCompletos = window.dadosCompletos;
            renderizarDashboard(data.data);
            
            // Atualiza data do último recebimento no header
            _atualizarUltimoRecebimentoOp(data.data);

            // Atualiza pagamentos completos
            if (data.data.ultimos_pagamentos) {
                window._pagamentosOperadorData = data.data.ultimos_pagamentos;
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
// ÚLTIMO RECEBIMENTO — HEADER (OPERADOR)
// ================================================================

function _atualizarUltimoRecebimentoOp(dados) {
    const el = document.getElementById('headerUltimoRecebimento');
    if (!el) return;

    // Pega a data mais recente dos pagamentos
    const pagamentos = dados.ultimos_pagamentos || [];
    if (pagamentos.length === 0) { el.textContent = ''; return; }

    // Ordena por data desc e pega o primeiro
    const sorted = [...pagamentos].sort((a, b) => {
        const dA = a.dtPgto || '';
        const dB = b.dtPgto || '';
        return dB.localeCompare(dA);
    });

    const ultima = sorted[0]?.dtPgto;
    if (!ultima || !ultima.includes('-')) { el.textContent = ''; return; }

    const partes = ultima.split('-');
    const dataFmt = `${partes[2]}/${partes[1]}/${partes[0]}`;
    el.innerHTML = `<i class="fas fa-clock" style="margin-right:4px;color:#a855f7;"></i>Últ. receb.: <strong>${dataFmt}</strong>`;
}

window._atualizarUltimoRecebimentoOp = _atualizarUltimoRecebimentoOp;

// ================================================================
// USUÁRIO
// ================================================================

function atualizarUsuario(operador) {
    if (!operador) return;
    
    const nome = operador.nome || 'Usuário';
    const primeiroNome = nome.split(' ')[0];
    const imagemUrl = operador.imagem || null;
    const iniciais = getIniciais(nome);
    const admissao = operador.admissao || null;
    const banco = operador.banco || 'Operador';
    
    // Calcula tempo de casa
    let tempoCasa = 'Tempo de casa: não disponível';
    if (admissao) {
        tempoCasa = calcularTempoCasa(admissao);
    }
    
    // Saudação personalizada no header
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) {
        pageTitle.textContent = `Olá, ${primeiroNome}!`;
    }
    
    // Nome e Banco no sidebar
    document.getElementById('userName').textContent = nome;
    document.getElementById('userRole').textContent = banco;
    
    // Avatar no sidebar
    const avatarText = document.getElementById('userAvatarText');
    const avatarImg = document.getElementById('userAvatarImg');
    
    if (imagemUrl && avatarImg) {
        avatarImg.src = imagemUrl;
        avatarImg.style.display = 'block';
        if (avatarText) avatarText.style.display = 'none';
    } else if (avatarText) {
        avatarText.textContent = iniciais;
        avatarText.style.display = 'flex';
        if (avatarImg) avatarImg.style.display = 'none';
    }

    // Avatar no header (Novo layout similar ao ADM)
    const headerText = document.getElementById('headerAvatarText');
    const headerImg = document.getElementById('headerAvatarImg');
    const headerName = document.getElementById('headerAvatarName');
    const headerRole = document.getElementById('headerAvatarRole');
    const headerTempo = document.getElementById('headerAvatarTempo');
    
    if (headerName) headerName.textContent = nome;
    if (headerRole) headerRole.textContent = banco;
    if (headerTempo) headerTempo.textContent = tempoCasa;

    // Busca o saldo do Banco de Horas do operador para o topo direito
    const userLogin = operador.login || operador.loguin;
    if (userLogin) {
        fetch(`/api/horarios/${userLogin}`)
            .then(res => res.json())
            .then(res => {
                if (res.success && res.data && res.data.ponto && res.data.ponto.card_d1) {
                    const saldo = res.data.ponto.card_d1.b_saldo || '00:00';
                    const cor = saldo.startsWith('-') ? '#ef4444' : '#10b981';
                    const elSaldoHeader = document.getElementById('headerBancoHorasSaldo');
                    if (elSaldoHeader) {
                        elSaldoHeader.innerHTML = `Banco de Horas: <span style="color:${cor};font-weight:800;">${saldo}</span>`;
                    }
                }
            })
            .catch(() => {});
    }

    if (imagemUrl && headerImg) {
        headerImg.src = imagemUrl;
        headerImg.style.display = 'block';
        if (headerText) headerText.style.display = 'none';
    } else if (headerText) {
        headerText.textContent = iniciais;
        headerText.style.display = 'flex';
        if (headerImg) headerImg.style.display = 'none';
    }


    // Ocultar filtro de Fase de Atraso na tela de Pagamentos se for AGORACRED
    const filtroFaseGrp = document.getElementById('filtro-pagamento-fase')?.closest('.filter-group');
    if (filtroFaseGrp) {
        if (banco === 'AGORACRED') {
            filtroFaseGrp.style.display = 'none';
        } else {
            filtroFaseGrp.style.display = 'flex';
        }
    }
}

// CALCULAR TEMPO DE CASA
// ================================================================

function calcularTempoCasa(admissao) {
    if (!admissao) return 'Tempo de casa: não disponível';

    try {
        const dataAdmissao = new Date(admissao);
        if (isNaN(dataAdmissao.getTime())) return 'Tempo de casa: data inválida';

        const hoje = new Date();
        let anos = hoje.getFullYear() - dataAdmissao.getFullYear();
        let meses = hoje.getMonth() - dataAdmissao.getMonth();
        let dias = hoje.getDate() - dataAdmissao.getDate();

        if (dias < 0) {
            meses--;
            const ultimoDiaMes = new Date(hoje.getFullYear(), hoje.getMonth(), 0).getDate();
            dias = ultimoDiaMes + dias;
        }

        if (meses < 0) {
            anos--;
            meses += 12;
        }

        return `Tempo de casa: ${anos} anos, ${meses} meses, ${dias} dias`;
    } catch (error) {
        console.error('Erro ao calcular tempo de casa:', error);
        return 'Tempo de casa: não disponível';
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
    
    // Atualiza título — preserva saudação personalizada no dashboard
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) {
        if (pagina === 'dashboard') {
            // Mantém a saudação já definida por atualizarUsuario
            // (não sobrescreve)
        } else {
            const titulos = {
                pagamentos: 'Pagamentos',
                clientes: 'Clientes',
                horarios: 'Horários / Ponto Eletrônico',
                performance: 'Performance',
                metas: 'Metas',
                campanhas: 'Campanhas'
            };
            pageTitle.textContent = titulos[pagina] || pagina;
        }
    }

    if (pagina === 'horarios' && typeof renderizarPontoOperador === 'function') {
        renderizarPontoOperador();
    }

    // Esconde a barra de filtros na página de horários (sempre puxa mês atual)
    const filtersBar = document.querySelector('.filters-bar');
    if (filtersBar) {
        filtersBar.style.display = pagina === 'horarios' ? 'none' : '';
    }
}


function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ================================================================
// FILTROS
// ================================================================

function filtrarDados() {
    const mes = document.getElementById('filtro-mes')?.value;
    const ano = document.getElementById('filtro-ano')?.value;

    // Sincroniza inputs ocultos das outras abas para que a recarga de dados utilize o mesmo mês/ano
    const pMes = document.getElementById('filtro-pagamento-mes');
    const pAno = document.getElementById('filtro-pagamento-ano');
    const oMes = document.getElementById('op-perf-mes');
    const oAno = document.getElementById('op-perf-ano');

    if (pMes && mes) pMes.value = mes;
    if (pAno && ano) pAno.value = ano;
    if (oMes && mes) oMes.value = mes;
    if (oAno && ano) oAno.value = ano;

    // Ao mudar o período (mês ou ano), reseta o filtro de faixas de atraso do operador
    const chkTodos = document.getElementById('chk-faixa-todas-op');
    if (chkTodos) {
        chkTodos.checked = true;
        const checkboxes = document.querySelectorAll('.chk-faixa-item-op');
        checkboxes.forEach(chk => {
            chk.checked = false;
        });
        const inputHidden = document.getElementById('filtro-faixa-op');
        if (inputHidden) inputHidden.value = 'todas';
        const labelSelected = document.getElementById('label-faixas-selecionadas-op');
        if (labelSelected) labelSelected.textContent = 'Todas as faixas';
    }

    carregarDados();
    const activePage = document.querySelector('.sidebar-nav li.active')?.getAttribute('data-page');
    if (activePage === 'operadores') {
        carregarPerformanceOp();
    }
}

// ================================================================
// LOADING / ERROR
// ================================================================

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

function showError(mensagem) {
    console.error('❌', mensagem);
    alert(mensagem);
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

async function carregarPerformanceOp() {
    try {
        const login = operadorLogado ? operadorLogado.login : null;
        if (!login) return;

        const mes = document.getElementById('filtro-mes')?.value || getMesAtual();
        const ano = document.getElementById('filtro-ano')?.value || getAnoAtual();

        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'flex';

        // Usa /api/resumo para ter indicadores_anterior, resultado_mes_a_mes e tma completos
        const response = await fetch(`${CONFIG.API_BASE}/resumo/${login}?mes=${mes}&ano=${ano}`);
        const data = await response.json();

        if (overlay) overlay.style.display = 'none';

        if (data.success) {
            // Monta estrutura compatível com renderizarMinhaPerformanceOp
            // que espera { performance, performance_diaria, resultado_mes_a_mes, indicadores_anterior }
            const dadosRenderizar = {
                performance: data.data.performance || {},
                performance_diaria: data.data.performance_diaria || data.data.faturamento_dia || [],
                resultado_mes_a_mes: data.data.resultado_mes_a_mes || [],
                indicadores_anterior: data.data.indicadores_anterior || {},
                tma: data.data.tma || {},
                ultimos_pagamentos: data.data.ultimos_pagamentos || [],
            };
            // Sincroniza pagamentos para a tabela semanal
            pagamentosRecentesOpData = dadosRenderizar.ultimos_pagamentos;
            pagamentosRecentesOpFiltrados = pagamentosRecentesOpData;
            renderizarMinhaPerformanceOp(dadosRenderizar);
        } else {
            console.error('Erro ao carregar performance do operador:', data.message);
        }
    } catch (error) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'none';
        console.error('Erro:', error);
    }
}


// Override navegar para carregar Performance quando ir para Operadores
// e sincronizar filtros ao entrar em Pagamentos
(function() {
    const _navegar = window.navegar;
    window.navegar = function(pagina) {
        _navegar(pagina);
        if (pagina === 'operadores') {
            carregarPerformanceOp();
        } else if (pagina === 'pagamentos') {
            // Sincroniza o mês/ano da aba de pagamentos com o filtro principal
            const mes = document.getElementById('filtro-mes')?.value || getMesAtual();
            const ano = document.getElementById('filtro-ano')?.value || getAnoAtual();
            const filtroPagMes = document.getElementById('filtro-pagamento-mes');
            const filtroPagAno = document.getElementById('filtro-pagamento-ano');
            if (filtroPagMes) filtroPagMes.value = mes;
            if (filtroPagAno) filtroPagAno.value = ano;
            // Recarrega os dados da aba de pagamentos com o período correto
            carregarDados();
        }
    };
})();

// ================================================================
// FILTRO DE PERÍODO NA PÁGINA PAGAMENTOS (mês/ano)
// ================================================================
// Antes, trocar o mês/ano só filtrava no navegador os dados já carregados
// (do mês selecionado no Dashboard), então podia "sobrar" pagamento de outro
// mês e o popup de carregando nunca aparecia. Agora isso dispara uma busca
// de verdade no servidor para o período escolhido.

async function filtrarPagamentosPeriodo() {
    const mes = document.getElementById('filtro-pagamento-mes')?.value;
    const ano = document.getElementById('filtro-pagamento-ano')?.value;

    const filtroMesPrincipal = document.getElementById('filtro-mes');
    const filtroAnoPrincipal = document.getElementById('filtro-ano');
    if (filtroMesPrincipal && mes) filtroMesPrincipal.value = mes;
    if (filtroAnoPrincipal && ano) filtroAnoPrincipal.value = ano;

    await carregarDados();
}
window.filtrarPagamentosPeriodo = filtrarPagamentosPeriodo;

// Funções globais para uso no HTML
window.navegar = navegar;
window.toggleSidebar = toggleSidebar;
window.filtrarDados = filtrarDados;
window.filtrarPagamentos = filtrarPagamentos;
window.carregarPerformanceOp = carregarPerformanceOp;
window.logout = logout;