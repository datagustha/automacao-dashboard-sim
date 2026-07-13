/**
 * APP ADM - Lógica Principal do ADM
 * ==================================
 */

// ================================================================
// CONFIGURAÇÃO
// ================================================================

const CONFIG_ADM = {
    API_BASE: '/api',
};

let dadosAdmCompletos = {};
let operadorAdmLogado = null;

// ================================================================
// INICIALIZAÇÃO
// ================================================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Dashboard V2 - ADM');

    // Verifica sessão
    const sessionData = await verificarSessaoAdm();
    if (!sessionData) {
        window.location.href = '/login';
        return;
    }

    operadorAdmLogado = sessionData;
    atualizarUsuarioAdm(operadorAdmLogado);

    // Configura mês e ano atual
    const mesAtual = getMesAtual();
    const anoAtual = getAnoAtual();

    const filtroMes = document.getElementById('filtro-mes-adm');
    const filtroAno = document.getElementById('filtro-ano-adm');

    if (filtroMes) filtroMes.value = mesAtual;
    if (filtroAno) filtroAno.value = anoAtual;

    // Atualiza data
    document.getElementById('currentDate').textContent = getDataAtual();

    // Carrega dados
    await carregarDadosAdm();

    // Configura eventos dos filtros principais
    if (filtroMes) filtroMes.addEventListener('change', carregarDadosAdm);
    if (filtroAno) filtroAno.addEventListener('change', carregarDadosAdm);

    // Configura logout
    const logoutBtn = document.querySelector('.btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logoutAdm);
    }
});

// ================================================================
// SESSÃO
// ================================================================

async function verificarSessaoAdm() {
    try {
        const response = await fetch('/api/session');
        const data = await response.json();
        if (data.success && data.data.banco === 'ADM') {
            return data.data;
        }
        return null;
    } catch (error) {
        console.error('Erro ao verificar sessão:', error);
        return null;
    }
}

// ================================================================
// CARREGAR DADOS COM LOADING
// ================================================================

async function carregarDadosAdm() {
    const overlay = document.getElementById('loading-overlay');

    try {
        // Mostra loading
        if (overlay) overlay.style.display = 'flex';

        const mes = document.getElementById('filtro-mes-adm')?.value || getMesAtual();
        const ano = document.getElementById('filtro-ano-adm')?.value || getAnoAtual();
        const atividade = document.getElementById('filtro-atividade-adm')?.value || 'ATIVO';
        const operador = document.getElementById('filtro-operador-adm')?.value || 'TODOS';
        const contrato = document.getElementById('filtro-contrato-adm')?.value || '';
        const faixa = document.getElementById('filtro-faixa-adm')?.value || 'todas';

        // Filtro de data range
        const dataInicio = document.getElementById('filtro-data-inicio-adm')?.value || '';
        const dataFim = document.getElementById('filtro-data-fim-adm')?.value || '';

        console.log('[ADM] Carregando dados com filtros:', { mes, ano, atividade, operador, contrato, faixa, dataInicio, dataFim });

        let url = `${CONFIG_ADM.API_BASE}/resumo-adm?mes=${mes}&ano=${ano}&atividade=${atividade}&operador=${encodeURIComponent(operador)}&contrato=${encodeURIComponent(contrato)}&faixa=${encodeURIComponent(faixa)}`;

        if (dataInicio) url += `&data_inicio=${dataInicio}`;
        if (dataFim) url += `&data_fim=${dataFim}`;

        const response = await fetch(url);
        const data = await response.json();

        // Esconde loading
        if (overlay) overlay.style.display = 'none';

        if (data.success) {
            dadosAdmCompletos = data.data;
            renderizarDashboardAdm(data.data);

            // Preenche dropdown de operadores
            preencherOperadores(data.data);

            // Preenche tabelas das páginas Pagamentos e Operadores
            renderizarPagamentosAdm(data.data);
            renderizarOperadoresAdm(data.data);
        } else {
            console.error('Erro ao carregar dados ADM:', data.message);
            showErrorAdm('Erro ao carregar dados: ' + data.message);
        }
    } catch (error) {
        // Esconde loading em caso de erro
        if (overlay) overlay.style.display = 'none';
        console.error('Erro:', error);
        showErrorAdm('Erro de conexão com o servidor');
    }
}

// ================================================================
// USUÁRIO COM FOTO E TEMPO DE CASA
// ================================================================

function atualizarUsuarioAdm(operador) {
    if (!operador) return;

    const nome = operador.nome || 'Administrador';
    const imagemUrl = operador.imagem || null;
    const iniciais = getIniciais(nome);
    const admissao = operador.admissao || null;

    // Calcula tempo de casa
    let tempoCasa = 'Tempo de casa: não disponível';
    if (admissao) {
        tempoCasa = calcularTempoCasa(admissao);
    }

    // Atualiza saudação no header
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) {
        const primeiroNome = nome.split(' ')[0];
        pageTitle.textContent = `Olá, ${primeiroNome}!`;
    }

    // Atualiza nome no sidebar
    document.getElementById('userName').textContent = nome;
    document.getElementById('userRole').textContent = 'Administrador';

    // Atualiza avatar no sidebar
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

    // Atualiza avatar no header
    const headerText = document.getElementById('headerAvatarText');
    const headerImg = document.getElementById('headerAvatarImg');
    const headerName = document.getElementById('headerAvatarName');
    const headerRole = document.getElementById('headerAvatarRole');
    const headerTempo = document.getElementById('headerAvatarTempo');

    if (headerName) headerName.textContent = nome;
    if (headerRole) headerRole.textContent = 'Administrador';
    if (headerTempo) headerTempo.textContent = tempoCasa;

    if (imagemUrl && headerImg) {
        headerImg.src = imagemUrl;
        headerImg.style.display = 'block';
        if (headerText) headerText.style.display = 'none';
    } else if (headerText) {
        headerText.textContent = iniciais;
        headerText.style.display = 'flex';
        if (headerImg) headerImg.style.display = 'none';
    }

    // Atualiza tempo de casa no sidebar (se tiver elemento)
    const tempoElement = document.getElementById('userTempoCasa');
    if (tempoElement) {
        tempoElement.textContent = tempoCasa;
    }

    console.log('[ADM] Usuário atualizado:', nome, 'Tempo de casa:', tempoCasa);
}

// ================================================================
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
// OPERADORES DROPDOWN
// ================================================================

function preencherOperadores(dados) {
    const select = document.getElementById('filtro-operador-adm');
    if (!select) return;

    // Salva valor selecionado atual
    const valorAtual = select.value;

    // Limpa opções (mantém a primeira)
    select.innerHTML = '<option value="TODOS">📊 Todos os Operadores</option>';

    const todosOperadores = [];

    // Correto: lê de dados.semear.operadores e dados.agoracred.operadores
    const opsSemear = dados.semear?.operadores || [];
    const opsAgoracred = dados.agoracred?.operadores || [];

    opsSemear.forEach(op => {
        if (op.login) {
            todosOperadores.push({
                login: op.login,
                nome: op.login,
                banco: 'SEMEAR'
            });
        }
    });

    opsAgoracred.forEach(op => {
        if (op.login) {
            todosOperadores.push({
                login: op.login,
                nome: op.login,
                banco: 'AGORACRED'
            });
        }
    });

    // Ordena por nome
    todosOperadores.sort((a, b) => a.nome.localeCompare(b.nome));

    todosOperadores.forEach(op => {
        const option = document.createElement('option');
        option.value = op.login;
        option.textContent = `${op.nome} (${op.banco})`;
        if (op.login === valorAtual) option.selected = true;
        select.appendChild(option);
    });

    console.log('[ADM] Dropdown de operadores preenchido com', todosOperadores.length, 'operadores');
}

// ================================================================
// RENDERIZAR PAGAMENTOS (ADM)
// ================================================================

function renderizarPagamentosAdm(dados) {
    const tbody = document.getElementById('tabela-pagamentos-adm');
    if (!tbody) return;

    // Coleta todos os pagamentos de ambos os bancos
    const todosPagamentos = [];

    const opsSemear = dados.semear?.operadores || [];
    const opsAgoracred = dados.agoracred?.operadores || [];

    // Como pagamentos_brutos são removidos antes do retorno, mostramos resumo por operador
    opsSemear.forEach(op => {
        if (op.faturamento > 0) {
            todosPagamentos.push({
                operador: op.login,
                banco: 'SEMEAR',
                faturamento: op.faturamento,
                operacoes: op.operacoes || '-',
                meta: op.meta,
                perc_meta: op.perc_meta
            });
        }
    });

    opsAgoracred.forEach(op => {
        if (op.faturamento > 0) {
            todosPagamentos.push({
                operador: op.login,
                banco: 'AGORACRED',
                faturamento: op.faturamento,
                operacoes: op.operacoes || '-',
                meta: op.meta,
                perc_meta: op.perc_meta
            });
        }
    });

    if (todosPagamentos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível no período</td></tr>';
        return;
    }

    // Ordena por faturamento decrescente
    todosPagamentos.sort((a, b) => (b.faturamento || 0) - (a.faturamento || 0));

    tbody.innerHTML = todosPagamentos.map(p => {
        const percMeta = p.perc_meta || 0;
        const corPerc = percMeta >= 100 ? '#10B981' : percMeta >= 70 ? '#d97706' : '#e74c3c';
        const bancoCor = p.banco === 'SEMEAR' ? '#7e3d97' : '#10B981';
        return `
            <tr>
                <td style="padding:10px 14px;text-align:center;">
                    <span style="background:${bancoCor};color:white;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">${p.banco}</span>
                </td>
                <td style="padding:10px 14px;text-align:center;font-weight:600;">${p.operador}</td>
                <td style="padding:10px 14px;text-align:center;font-weight:700;">${formatarMoeda(p.faturamento)}</td>
                <td style="padding:10px 14px;text-align:center;">${formatarMoeda(p.meta)}</td>
                <td style="padding:10px 14px;text-align:center;font-weight:700;color:${corPerc};">${percMeta.toFixed(1)}%</td>
            </tr>
        `;
    }).join('');
}

// ================================================================
// RENDERIZAR OPERADORES (ADM)
// ================================================================

function renderizarOperadoresAdm(dados) {
    const tbody = document.getElementById('tabela-operadores-adm');
    if (!tbody) return;

    const todos = [];
    const opsSemear = dados.semear?.operadores || [];
    const opsAgoracred = dados.agoracred?.operadores || [];

    opsSemear.forEach(op => todos.push({ ...op, banco: 'SEMEAR' }));
    opsAgoracred.forEach(op => todos.push({ ...op, banco: 'AGORACRED' }));

    if (todos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#6B7280;padding:30px;">Nenhum operador disponível</td></tr>';
        return;
    }

    tbody.innerHTML = todos.map(op => {
        const bancoCor = op.banco === 'SEMEAR' ? '#7e3d97' : '#10B981';
        const fotoHtml = op.imagem
            ? `<img src="${op.imagem}" alt="${op.login}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:2px solid ${bancoCor};">`
            : `<div style="width:32px;height:32px;border-radius:50%;background:${bancoCor};color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">${(op.login||'').replace(/[0-9]/g,'').substring(0,2).toUpperCase()}</div>`;

        return `
            <tr>
                <td class="sticky-col-1" style="padding:8px 12px;text-align:center;">${fotoHtml}</td>
                <td class="sticky-col-3" style="padding:8px 12px;text-align:center;font-weight:600;">${op.login || '-'}</td>
                <td style="padding:8px 12px;text-align:center;">
                    <span style="background:${bancoCor};color:white;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">${op.banco}</span>
                </td>
                <td style="padding:8px 12px;text-align:center;">${op.turno || '-'}</td>
                <td style="padding:8px 12px;text-align:center;font-size:11px;white-space:nowrap;">${op.tempo_casa || '-'}</td>
                <td style="padding:8px 12px;text-align:center;font-weight:700;">${formatarMoeda(op.faturamento || 0)}</td>
                <td style="padding:8px 12px;text-align:center;font-weight:700;color:${(op.perc_meta||0) >= 100 ? '#10B981' : '#e74c3c'};">${(op.perc_meta||0).toFixed(1)}%</td>
            </tr>
        `;
    }).join('');
}

// ================================================================
// NAVEGAÇÃO
// ================================================================

function navegar(pagina) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    const pageElement = document.getElementById(`page-${pagina}`);
    if (pageElement) pageElement.classList.add('active');

    document.querySelectorAll('.sidebar-nav li').forEach(li => li.classList.remove('active'));
    const menuItem = document.querySelector(`.sidebar-nav li[data-page="${pagina}"]`);
    if (menuItem) menuItem.classList.add('active');

    const titulos = {
        dashboard: 'Dashboard ADM',
        pagamentos: 'Pagamentos',
        operadores: 'Operadores'
    };
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) pageTitle.textContent = titulos[pagina] || pagina;
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ================================================================
// ERROR
// ================================================================

function showErrorAdm(mensagem) {
    console.error('❌', mensagem);
}

// ================================================================
// LOGOUT
// ================================================================

async function logoutAdm() {
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
// FILTROS ADM
// ================================================================

function filtrarAdm() {
    const contrato = document.getElementById('filtro-contrato-adm')?.value || '';
    const faixa = document.getElementById('filtro-faixa-adm')?.value || 'todas';

    const badge = document.getElementById('badge-filtros-ativos-adm');
    if (badge) {
        if (contrato || faixa !== 'todas') {
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }

    carregarDadosAdm();
}

// ================================================================
// EXPORT
// ================================================================

window.navegar = navegar;
window.toggleSidebar = toggleSidebar;
window.carregarDadosAdm = carregarDadosAdm;
window.filtrarAdm = filtrarAdm;
window.logout = logoutAdm;

// ================================================================
// TMA ADM - Carregamento e Renderização
// ================================================================

async function carregarTmaAdm() {
    const tbody = document.getElementById('tabela-tma-adm');
    if (!tbody) return;

    try {
        const mes = document.getElementById('filtro-mes-adm')?.value || getMesAtual();
        const ano = document.getElementById('filtro-ano-adm')?.value || getAnoAtual();
        const atividade = document.getElementById('filtro-atividade-adm')?.value || 'ATIVO';

        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#6B7280;padding:20px;"><i class="fas fa-spinner fa-spin"></i> Carregando TMA...</td></tr>';

        const url = `/api/tma-adm?mes=${mes}&ano=${ano}&atividade=${atividade}`;
        const resp = await fetch(url);
        const data = await resp.json();

        if (data.success) {
            renderizarTmaAdm(data.data || []);
        } else {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;color:#e74c3c;padding:20px;">Erro ao carregar TMA: ${data.message || 'desconhecido'}</td></tr>`;
        }
    } catch (err) {
        const tbody2 = document.getElementById('tabela-tma-adm');
        if (tbody2) tbody2.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#e74c3c;padding:20px;">Erro de conexão ao carregar TMA.</td></tr>';
        console.error('[TMA ADM]', err);
    }
}

function renderizarTmaAdm(lista) {
    const tbody = document.getElementById('tabela-tma-adm');
    if (!tbody) return;

    if (!lista || lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado de TMA disponível para o período selecionado.<br><small>Verifique se o arquivo CSV de TMA foi importado.</small></td></tr>';
        return;
    }

    let totalAcionamentos = 0;
    let totalClientes = 0;

    const linhas = lista.map((op, idx) => {
        const bancoCor = op.banco === 'SEMEAR' ? '#7e3d97' : '#10B981';
        const foto = op.imagem
            ? `<img src="${op.imagem}" alt="${op.login}" style="width:34px;height:34px;border-radius:50%;object-fit:cover;border:2px solid ${bancoCor};">`
            : `<div style="width:34px;height:34px;border-radius:50%;background:${bancoCor};color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;margin:0 auto;">${(op.login||'').replace(/[0-9]/g,'').substring(0,2).toUpperCase()}</div>`;

        totalAcionamentos += Number(op.acionamentos || 0);
        totalClientes += Number(op.clientes || 0);

        // Badge de posição
        let pos = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx+1}°`;

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-3" style="text-align:center;padding:8px 10px;font-weight:600;">
                    <span style="margin-right:6px;font-size:13px;">${pos}</span>${op.login || '-'}
                    <br><span style="background:${bancoCor};color:white;padding:1px 8px;border-radius:10px;font-size:10px;font-weight:600;">${op.banco}</span>
                </td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;font-family:monospace;font-size:14px;">${op.tma || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:#0891b2;">${op.acionamentos || 0}</td>
                <td style="text-align:center;padding:8px 10px;">${op.clientes || 0}</td>
                <td style="text-align:center;padding:8px 10px;font-size:12px;">${op.reacionamento || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-family:monospace;">${op.tempo_falado || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;color:var(--text-muted);">${op.primeiro_acionamento || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;color:var(--text-muted);">${op.ultimo_acionamento || '-'}</td>
            </tr>
        `;
    }).join('');

    // Linha de totais
    const totalRow = `
        <tr style="background:#e0f2fe;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;"></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#0369a1;"><strong>📊 TOTAL</strong></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#0369a1;font-size:15px;">${totalAcionamentos}</td>
            <td style="text-align:center;padding:10px;color:#0369a1;">${totalClientes}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
        </tr>
    `;

    tbody.innerHTML = linhas + totalRow;
}

// Override navegar para carregar TMA quando ir para Operadores
(function() {
    const _navegar = window.navegar;
    window.navegar = function(pagina) {
        _navegar(pagina);
        if (pagina === 'operadores') {
            carregarTmaAdm();
        }
    };
})();