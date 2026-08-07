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
let todosOperadoresCadastrados = [];
window.todosOperadoresCadastrados = todosOperadoresCadastrados;

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
    window.operadorAdmLogado = operadorAdmLogado; // Expõe globalmente para dashboard_adm.js
    atualizarUsuarioAdm(operadorAdmLogado);

    // Configura mês e ano atual
    const mesAtual = getMesAtual();
    const anoAtual = getAnoAtual();

    const idsMes = ['filtro-mes-adm', 'filtro-pag-mes-adm', 'filtro-mes-adm-op'];
    const idsAno = ['filtro-ano-adm', 'filtro-pag-ano-adm', 'filtro-ano-adm-op'];

    function sincronizarPeriodoAdm(mes, ano) {
        idsMes.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = mes;
        });
        idsAno.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = ano;
        });
    }

    sincronizarPeriodoAdm(mesAtual, anoAtual);

    // Atualiza data
    document.getElementById('currentDate').textContent = getDataAtual();

    // Carrega dados
    await carregarDadosAdm();

    // Auto-atualização a cada 10 minutos para capturar novos pagamentos
    setInterval(() => {
        carregarDadosAdm();
    }, 600000);

    // Configura eventos dos filtros de período sincronizados
    idsMes.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', function() {
                const mes = this.value;
                const ano = document.getElementById('filtro-ano-adm')?.value || getAnoAtual();
                sincronizarPeriodoAdm(mes, ano);
                carregarDadosAdm();
            });
        }
    });

    idsAno.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', function() {
                const mes = document.getElementById('filtro-mes-adm')?.value || getMesAtual();
                const ano = this.value;
                sincronizarPeriodoAdm(mes, ano);
                carregarDadosAdm();
            });
        }
    });

    // Configura evento do filtro de operador global do topo
    const selGlobal = document.getElementById('filtro-operador-adm');
    if (selGlobal) {
        selGlobal.addEventListener('change', function() {
            const login = this.value;
            const selPerf = document.getElementById('filtro-operador-perf-adm');
            if (selPerf) {
                if (login === 'TODOS') {
                    if (selPerf.value !== '' && selPerf.value !== 'CONSOLIDADO_SEMEAR' && selPerf.value !== 'CONSOLIDADO_AGORACRED') {
                        selPerf.value = 'CONSOLIDADO_SEMEAR';
                        selecionarOperadorPerfAdm();
                    }
                } else {
                    if (selPerf.value !== login) {
                        selPerf.value = login;
                        selecionarOperadorPerfAdm();
                    }
                }
            }
            carregarDadosAdm();
        });
    }

    // Configura evento de atividade
    const selAtividade = document.getElementById('filtro-atividade-adm');
    if (selAtividade) {
        selAtividade.addEventListener('change', carregarDadosAdm);
    }

    // Configura logout
    const logoutBtn = document.querySelector('.btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logoutAdm);
    }

    // Inicialização do controle de horários/ponto da equipe (ADM)
    if (typeof carregarPontoAdm === 'function') {
        carregarPontoAdm();
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
        const banco = document.getElementById('filtro-banco-adm')?.value || 'TODOS';

        // Filtro de data range
        const dataInicio = document.getElementById('filtro-data-inicio-adm')?.value || '';
        const dataFim = document.getElementById('filtro-data-fim-adm')?.value || '';
        // Filtro global de Dia Útil — filtra toda a página pelo intervalo (ex: 1 a 15 DU)
        const duInicio = document.getElementById('filtro-du-inicio-adm')?.value || '';
        const duFim = document.getElementById('filtro-du-fim-adm')?.value || '';

        console.log('[ADM] Carregando dados com filtros:', { mes, ano, atividade, operador, contrato, faixa, banco, dataInicio, dataFim, duInicio, duFim });

        let url = `${CONFIG_ADM.API_BASE}/resumo-adm?mes=${mes}&ano=${ano}&atividade=${atividade}&operador=${encodeURIComponent(operador)}&contrato=${encodeURIComponent(contrato)}&faixa=${encodeURIComponent(faixa)}&banco=${encodeURIComponent(banco)}`;

        if (dataInicio) url += `&data_inicio=${dataInicio}`;
        if (dataFim) url += `&data_fim=${dataFim}`;
        if (duInicio) url += `&du_inicio=${duInicio}`;
        if (duFim) url += `&du_fim=${duFim}`;


        const response = await fetch(url);
        if (response.status === 401) {
            console.warn('[ADM] Sessão expirada ou não autorizada. Redirecionando para login...');
            window.location.href = '/login';
            return;
        }
        const data = await response.json();


        // Esconde loading
        if (overlay) overlay.style.display = 'none';

        if (data.success) {
            dadosAdmCompletos = data.data;
            renderizarDashboardAdm(data.data);
            carregarTmaAdm();

            // Atualiza data do último recebimento no header
            _atualizarUltimoRecebimentoAdm(data.data);

            // Mostra / Esconde o banner de operador filtrado no Dashboard
            const bannerDash = document.getElementById('banner-operador-selecionado-dashboard-adm');
            if (bannerDash) {
                if (operador !== 'TODOS') {
                    // Tenta achar operador na lista global
                    const opCadastrado = (todosOperadoresCadastrados || []).find(o => o.login === operador);
                    const nomeExibicao = opCadastrado?.login || operador;
                    const tempoCasaExib = opCadastrado?.tempo_casa || 'Tempo de casa não informado';
                    const imgUrl = opCadastrado?.imagem || null;
                    const bancoOp = opCadastrado?.banco || 'SEMEAR';

                    document.getElementById('banner-op-nome-dash').textContent = nomeExibicao;
                    document.getElementById('banner-op-info-dash').textContent = `${bancoOp} • ${tempoCasaExib}`;
                    
                    const avatarTxt = document.getElementById('banner-op-avatar-txt-dash');
                    const avatarImg = document.getElementById('banner-op-avatar-img-dash');
                    if (imgUrl) {
                        if (avatarImg) {
                            avatarImg.src = imgUrl;
                            avatarImg.style.display = 'block';
                        }
                        if (avatarTxt) avatarTxt.style.display = 'none';
                    } else {
                        if (avatarTxt) {
                            avatarTxt.textContent = nomeExibicao.replace(/[0-9]/g, '').substring(0, 2).toUpperCase() || 'OP';
                            avatarTxt.style.display = 'flex';
                        }
                        if (avatarImg) avatarImg.style.display = 'none';
                    }
                    bannerDash.style.display = 'flex';
                } else {
                    bannerDash.style.display = 'none';
                }
            }

            // Preenche dropdown de operadores
            preencherOperadores(data.data);

            // Preenche tabelas das páginas Pagamentos e Operadores
            if (typeof carregarPagamentosAdm === 'function') {
                carregarPagamentosAdm();
            }
            renderizarOperadoresAdm(data.data);

            // Pivot Mês × Operador
            window._pivotSemear    = (data.data.semear    || {}).pivot_mes_operador || [];
            window._pivotAgoracred = (data.data.agoracred || {}).pivot_mes_operador || [];
            if (typeof renderizarMesOperadorAdm === 'function') {
                renderizarMesOperadorAdm(window._pivotSemear, 'SEMEAR');
            }
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
// ÚLTIMO RECEBIMENTO — HEADER
// ================================================================

function _atualizarUltimoRecebimentoAdm(dados) {
    const el = document.getElementById('headerUltimoRecebimento');
    if (!el) return;

    const uSemear = dados.semear?.ultima_baixa;
    const uAgora = dados.agoracred?.ultima_baixa;

    let maiorData = uSemear || uAgora || '';
    if (uSemear && uAgora) {
        const pS = uSemear.split('/').reverse().join('');
        const pA = uAgora.split('/').reverse().join('');
        maiorData = pS >= pA ? uSemear : uAgora;
    }

    if (!maiorData) {
        el.textContent = '';
        return;
    }

    el.innerHTML = `<i class="fas fa-clock" style="margin-right:4px;color:#7E3E9A;"></i>Últ. receb.: <strong>${maiorData}</strong>`;
}

function limparFiltrosTodosAdm() {
    // Reseta filtros do Dashboard
    const filtroMes = document.getElementById('filtro-mes-adm');
    const filtroAno = document.getElementById('filtro-ano-adm');
    const filtroBanco = document.getElementById('filtro-banco-adm');
    const filtroAtiv = document.getElementById('filtro-atividade-adm');
    const sel = document.getElementById('filtro-operador-adm');
    const inicio = document.getElementById('filtro-data-inicio-adm');
    const fim = document.getElementById('filtro-data-fim-adm');
    const contrato = document.getElementById('filtro-contrato-adm');
    const faixa = document.getElementById('filtro-faixa-adm');
    const duInicio = document.getElementById('filtro-du-inicio-adm');
    const duFim = document.getElementById('filtro-du-fim-adm');

    const hoje = new Date();
    if (filtroMes) filtroMes.value = hoje.getMonth() + 1;
    if (filtroAno) filtroAno.value = hoje.getFullYear();
    if (filtroBanco) filtroBanco.value = 'TODOS';
    if (filtroAtiv) filtroAtiv.value = 'ATIVO';
    if (sel) sel.value = 'TODOS';
    if (inicio) inicio.value = '';
    if (fim) fim.value = '';
    if (contrato) contrato.value = '';
    if (faixa) faixa.value = 'todas';
    if (duInicio) duInicio.value = '';
    if (duFim) duFim.value = '';

    // Reseta os checkboxes do multiselect de faixas
    const chkFaixaTodas = document.getElementById('chk-faixa-todas');
    if (chkFaixaTodas) chkFaixaTodas.checked = true;
    document.querySelectorAll('.chk-faixa-item').forEach(chk => chk.checked = false);
    const labelFaixas = document.getElementById('label-faixas-selecionadas');
    if (labelFaixas) labelFaixas.textContent = 'Todas as faixas';

    // Reseta os checkboxes do multiselect de operadores
    const chkOperadorTodos = document.getElementById('chk-operador-todos');
    if (chkOperadorTodos) chkOperadorTodos.checked = true;
    document.querySelectorAll('.chk-operador-item').forEach(chk => chk.checked = false);
    const labelOperadores = document.getElementById('label-operadores-selecionados');
    if (labelOperadores) labelOperadores.textContent = 'Todos os Operadores';

    const badge = document.getElementById('badge-filtros-ativos-adm');
    if (badge) badge.style.display = 'none';

    const bannerDash = document.getElementById('banner-operador-selecionado-dashboard-adm');
    if (bannerDash) bannerDash.style.display = 'none';

    // Limpa também o filtro de datas
    const badgeData = document.getElementById('badge-data-range-adm');
    if (badgeData) { badgeData.textContent = ''; badgeData.style.display = 'none'; }
    const ei = document.getElementById('filtro-data-inicio-adm');
    const ef = document.getElementById('filtro-data-fim-adm');
    if (ei) ei.value = '';
    if (ef) ef.value = '';

    carregarDadosAdm();
}

function aplicarFiltroDatasAdm() {
    const inicio = document.getElementById('filtro-data-inicio-adm')?.value;
    const fim = document.getElementById('filtro-data-fim-adm')?.value;
    const badge = document.getElementById('badge-data-range-adm');
    if (!inicio && !fim) {
        alert('Selecione ao menos uma data para filtrar.');
        return;
    }
    if (badge) {
        const fmt = v => v ? v.split('-').reverse().join('/') : '';
        badge.textContent = `📅 ${fmt(inicio) || '...'} → ${fmt(fim) || '...'}`;
        badge.style.display = 'inline-block';
    }
    // Sincroniza com inputs locais da página de Pagamentos e dispara o carregamento correto
    const elPagInicio = document.getElementById('filtro-pag-inicio-adm');
    const elPagFim = document.getElementById('filtro-pag-fim-adm');
    if (elPagInicio) elPagInicio.value = inicio || '';
    if (elPagFim) elPagFim.value = fim || '';
    if (typeof carregarPagamentosAdm === 'function') carregarPagamentosAdm();
    carregarDadosAdm();
}

function limparFiltroDatasAdm() {
    const ei = document.getElementById('filtro-data-inicio-adm');
    const ef = document.getElementById('filtro-data-fim-adm');
    const badge = document.getElementById('badge-data-range-adm');
    const duInicio = document.getElementById('filtro-du-inicio-adm');
    const duFim = document.getElementById('filtro-du-fim-adm');
    if (ei) ei.value = '';
    if (ef) ef.value = '';
    if (duInicio) duInicio.value = '';
    if (duFim) duFim.value = '';
    if (badge) { badge.textContent = ''; badge.style.display = 'none'; }

    // Limpa também os inputs locais da página de Pagamentos
    const elPagInicio = document.getElementById('filtro-pag-inicio-adm');
    const elPagFim = document.getElementById('filtro-pag-fim-adm');
    if (elPagInicio) elPagInicio.value = '';
    if (elPagFim) elPagFim.value = '';
    if (typeof carregarPagamentosAdm === 'function') carregarPagamentosAdm();
    carregarDadosAdm();
}

function limparFiltrosPagAdm() {
    const filtroPagMes = document.getElementById('filtro-pag-mes-adm');
    const filtroPagAno = document.getElementById('filtro-pag-ano-adm');
    const filtroPagBanco = document.getElementById('filtro-pag-banco-adm');
    const filtroPagAtiv = document.getElementById('filtro-pag-atividade-adm');
    const busca = document.getElementById('busca-pag-operador-adm');
    const sel = document.getElementById('filtro-pag-operador-adm');
    const busca2 = document.getElementById('filtro-pag-busca-adm');
    const fase = document.getElementById('filtro-pag-fase-adm');
    const inicio = document.getElementById('filtro-pag-inicio-adm');
    const fim = document.getElementById('filtro-pag-fim-adm');

    const hoje = new Date();
    if (filtroPagMes) filtroPagMes.value = hoje.getMonth() + 1;
    if (filtroPagAno) filtroPagAno.value = hoje.getFullYear();
    if (filtroPagBanco) filtroPagBanco.value = 'TODOS';
    if (filtroPagAtiv) filtroPagAtiv.value = 'ATIVO';
    if (busca) busca.value = '';
    if (sel) sel.value = 'TODOS';
    if (busca2) busca2.value = '';
    if (fase) fase.value = '';
    if (inicio) inicio.value = '';
    if (fim) fim.value = '';

    carregarPagamentosAdm();
}

function limparFiltrosOpAdm() {
    voltarConsolidadoAdm();
}

window.limparFiltrosTodosAdm = limparFiltrosTodosAdm;
window.limparFiltrosPagAdm = limparFiltrosPagAdm;
window.limparFiltrosOpAdm = limparFiltrosOpAdm;

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

    // Busca o saldo do banco de horas do usuário logado para exibir no topo direito
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

// Cache global persistente para operadores
if (!window._cacheOperadoresCompletos) {
    window._cacheOperadoresCompletos = {
        SEMEAR: new Set(),
        AGORACRED: new Set()
    };
}

function preencherOperadores(dados) {
    const container = document.getElementById('options-operadores-container');
    const inputHidden = document.getElementById('filtro-operador-adm');
    const labelSelected = document.getElementById('label-operadores-selecionados');
    if (!container) return;

    // Limpa o campo de busca do segmentador ao reconstruir a lista
    const inputPesquisa = document.getElementById('pesquisa-operador-input');
    if (inputPesquisa) inputPesquisa.value = '';

    // Se o filtro de operador estiver no padrão (TODOS), limpa o cache para que a mudança
    // do filtro de atividade (Ativo/Inativo) recrie a lista corretamente com base no payload da API.
    const operadorFiltroAtivo = inputHidden ? inputHidden.value : 'TODOS';
    if (operadorFiltroAtivo === 'TODOS') {
        window._cacheOperadoresCompletos.SEMEAR.clear();
        window._cacheOperadoresCompletos.AGORACRED.clear();
    }

    // Alimenta o cache com os operadores que vieram no payload atual
    if (dados.semear?.operadores) {
        dados.semear.operadores.forEach(op => {
            if (op.login) window._cacheOperadoresCompletos.SEMEAR.add(op.login);
        });
    }
    if (dados.agoracred?.operadores) {
        dados.agoracred.operadores.forEach(op => {
            if (op.login) window._cacheOperadoresCompletos.AGORACRED.add(op.login);
        });
    }

    // Obtém o banco selecionado no filtro do Dashboard
    const bancoSelecionado = document.getElementById('filtro-banco-adm')?.value || 'TODOS';

    // Salva quais estavam previamente selecionados para persistir a seleção do usuário
    const valoresPreviamenteSelecionados = inputHidden && inputHidden.value !== 'TODOS'
        ? inputHidden.value.split(',')
        : [];

    const todosOperadores = [];

    // Constrói a lista a partir do cache persistente para que a lista não encolha
    if (bancoSelecionado === 'TODOS' || bancoSelecionado === 'SEMEAR') {
        window._cacheOperadoresCompletos.SEMEAR.forEach(login => {
            todosOperadores.push({
                login: login,
                nome: login,
                banco: 'SEMEAR'
            });
        });
    }

    if (bancoSelecionado === 'TODOS' || bancoSelecionado === 'AGORACRED') {
        window._cacheOperadoresCompletos.AGORACRED.forEach(login => {
            todosOperadores.push({
                login: login,
                nome: login,
                banco: 'AGORACRED'
            });
        });
    }

    // Ordena por nome
    todosOperadores.sort((a, b) => a.nome.localeCompare(b.nome));

    // Se a lista estiver vazia
    if (todosOperadores.length === 0) {
        container.innerHTML = '<div style="padding:8px;text-align:center;color:#9ca3af;font-size:11px;">Nenhum operador encontrado</div>';
        return;
    }

    container.innerHTML = todosOperadores.map(op => {
        const checked = valoresPreviamenteSelecionados.includes(op.login) ? 'checked' : '';
        const corBanco = op.banco === 'SEMEAR' ? '#7e3d97' : '#10b981';
        return `
            <label style="display:flex;align-items:center;gap:8px;padding:4px 8px;font-size:12px;color:#374151;cursor:pointer;width:100%;box-sizing:border-box;margin:0;">
                <input type="checkbox" class="chk-operador-item" value="${op.login}" ${checked} onchange="atualizarSelecaoOperadores()">
                <span style="white-space:nowrap;">${op.nome}</span>
                <span style="font-size:9px;background:${corBanco}20;color:${corBanco};padding:1px 6px;border-radius:10px;font-weight:600;margin-left:auto;white-space:nowrap;">${op.banco}</span>
            </label>
        `;
    }).join('');

    // Sincroniza a label e o input oculto sem disparar nova recarga (evita loop infinito)
    atualizarSelecaoOperadores(true);
}

/**
 * Filtra dinamicamente a lista de operadores exibida no segmentador de acordo com o termo digitado.
 *
 * @param {string} termo - O termo de busca digitado pelo usuário
 */
function filtrarOperadoresDropdown(termo) {
    const termoLower = termo.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const container = document.getElementById('options-operadores-container');
    if (!container) return;
    
    const labels = container.querySelectorAll('label');
    labels.forEach(label => {
        const span = label.querySelector('span');
        const text = span ? span.textContent : (label.textContent || '');
        const textLower = text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        
        if (textLower.includes(termoLower)) {
            label.style.setProperty('display', 'flex', 'important');
        } else {
            label.style.setProperty('display', 'none', 'important');
        }
    });
}

/**
 * Gerencia o comportamento quando a opção "Todos os Operadores" é marcada/desmarcada.
 * Se marcada, desmarca todos os operadores específicos.
 *
 * @param {HTMLInputElement} chkTodos - O checkbox "Todos os Operadores"
 */
function toggleTodosOperadores(chkTodos) {
    const checkboxes = document.querySelectorAll('.chk-operador-item');
    if (chkTodos.checked) {
        // Desmarca todas as opções individuais
        checkboxes.forEach(chk => {
            chk.checked = false;
        });
    }
    atualizarSelecaoOperadores();
}

/**
 * Atualiza o estado da seleção múltipla de operadores.
 * Coleta os logins selecionados, atualiza o campo oculto que é lido pelo app_adm.js,
 * ajusta o rótulo do botão para refletir as seleções e dispara a recarga de dados do painel.
 *
 * @param {boolean} evitarRecarga - Se true, não dispara a chamada de API de recarga de dados
 */
function atualizarSelecaoOperadores(evitarRecarga = false) {
    const chkTodos = document.getElementById('chk-operador-todos');
    const chkItems = document.querySelectorAll('.chk-operador-item');
    const inputHidden = document.getElementById('filtro-operador-adm');
    const labelSelected = document.getElementById('label-operadores-selecionados');
    
    const selecionados = [];
    chkItems.forEach(chk => {
        if (chk.checked) selecionados.push(chk.value);
    });
    
    if (selecionados.length > 0) {
        // Se há opções individuais marcadas, desmarca o checkbox "Todos"
        if (chkTodos) chkTodos.checked = false;
        
        // Junta os logins por vírgula para passar como parâmetro na API
        const valorFiltro = selecionados.join(',');
        if (inputHidden) inputHidden.value = valorFiltro;
        
        // Atualiza a label do botão
        if (labelSelected) {
            if (selecionados.length <= 2) {
                labelSelected.textContent = selecionados.join(', ');
            } else {
                labelSelected.textContent = `${selecionados.length} selecionados`;
            }
        }
    } else {
        // Se nada específico estiver marcado, marca o "Todos os Operadores" como fallback
        if (chkTodos) chkTodos.checked = true;
        if (inputHidden) inputHidden.value = 'TODOS';
        if (labelSelected) labelSelected.textContent = 'Todos os Operadores';
    }
    
    // Atualiza a visualização no badge de filtros ativos
    const badgFiltros = document.getElementById('badge-filtros-ativos-adm');
    const contratoVal = document.getElementById('filtro-contrato-adm')?.value || '';
    const faixaVal = document.getElementById('filtro-faixa-adm')?.value || 'todas';
    const operadorVal = inputHidden ? inputHidden.value : 'TODOS';
    
    if (badgFiltros) {
        if (contratoVal || faixaVal !== 'todas' || operadorVal !== 'TODOS') {
            badgFiltros.style.display = 'inline-block';
        } else {
            badgFiltros.style.display = 'none';
        }
    }
    
    // Dispara a chamada API de recarga
    if (!evitarRecarga && typeof carregarDadosAdm === 'function') {
        carregarDadosAdm();
    }
}

// Event listener global para fechar o dropdown ao clicar fora do componente de operadores
document.addEventListener('click', function(event) {
    const container = document.getElementById('multiselect-operador-adm');
    const content = document.getElementById('dropdown-operadores-content');
    if (container && content && !container.contains(event.target)) {
        content.style.display = 'none';
    }
});

// Registra funções no escopo global/window
window.preencherOperadores        = preencherOperadores;
window.toggleTodosOperadores       = toggleTodosOperadores;
window.atualizarSelecaoOperadores  = atualizarSelecaoOperadores;


// Funções globais de busca inteligente com autocomplete para os filtros de todas as páginas
function onBuscaOperadorGlobal(valor) {
    const sel = document.getElementById('filtro-operador-adm');
    if (!sel) return;

    if (!valor || valor.trim() === '' || valor.toUpperCase() === 'TODOS') {
        sel.value = 'TODOS';
        const event = new Event('change');
        sel.dispatchEvent(event);
        return;
    }

    const valorUpper = valor.trim().toUpperCase();
    const optMatch = Array.from(sel.options).find(opt => 
        opt.value.toUpperCase() === valorUpper
    );

    if (optMatch) {
        sel.value = optMatch.value;
        const event = new Event('change');
        sel.dispatchEvent(event);
    }
}

function onBuscaOperadorPag(valor) {
    const sel = document.getElementById('filtro-pag-operador-adm');
    if (!sel) return;

    if (!valor || valor.trim() === '' || valor.toUpperCase() === 'TODOS') {
        sel.value = 'TODOS';
        carregarPagamentosAdm();
        return;
    }

    const valorUpper = valor.trim().toUpperCase();
    const optMatch = Array.from(sel.options).find(opt => 
        opt.value.toUpperCase() === valorUpper
    );

    if (optMatch) {
        sel.value = optMatch.value;
        carregarPagamentosAdm();
    }
}

// Expõe globalmente
window.onBuscaOperadorGlobal = onBuscaOperadorGlobal;
window.onBuscaOperadorPag = onBuscaOperadorPag;

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
        const corPerc = percMeta >= 100 ? '#10B981' : '#7e3d97';
        const bancoCor = p.banco === 'SEMEAR' ? '#7e3d97' : '#10B981';

        // Barra de progresso para a célula
        const progressoHtml = `
            <div class="table-progress-container" style="min-width:110px;">
                <div class="table-progress-bar">
                    <div class="table-progress-fill ${p.banco === 'SEMEAR' ? 'purple' : 'green'}" style="width: ${Math.min(percMeta, 100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color: ${bancoCor};">${percMeta.toFixed(1)}%</span>
            </div>
        `;

        return `
            <tr>
                <td class="sticky-col-1" style="padding:10px 14px;text-align:center;">
                    <span style="background:${bancoCor};color:white;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">${p.banco}</span>
                </td>
                <td class="sticky-col-3" style="padding:10px 14px;text-align:center;font-weight:600;color:var(--text-main);">${p.operador}</td>
                <td style="padding:10px 14px;text-align:center;font-weight:700;">${formatarMoeda(p.faturamento)}</td>
                <td style="padding:10px 14px;text-align:center;">${formatarMoeda(p.meta)}</td>
                <td style="padding:10px 14px;text-align:center;">${progressoHtml}</td>
            </tr>
        `;
    }).join('');

    // Linha de Total consolidada
    const totalFat = todosPagamentos.reduce((s, p) => s + (p.faturamento || 0), 0);
    const totalMeta = todosPagamentos.reduce((s, p) => s + (p.meta || 0), 0);
    const totalPerc = totalMeta > 0 ? (totalFat / totalMeta) * 100 : 0;

    const progressoTotalHtml = `
        <div class="table-progress-container" style="min-width:110px;">
            <div class="table-progress-bar">
                <div class="table-progress-fill purple" style="width: ${Math.min(totalPerc, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: var(--purple-main);">${totalPerc.toFixed(1)}%</span>
        </div>
    `;

    const trTotal = `
        <tr class="sticky-total-row">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:var(--purple-main);"><strong>TOTAL</strong></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:var(--purple-main);"></td>
            <td style="text-align:center;padding:10px;color:var(--purple-main);font-weight:700;">${formatarMoeda(totalFat)}</td>
            <td style="text-align:center;padding:10px;color:var(--purple-main);">${formatarMoeda(totalMeta)}</td>
            <td style="text-align:center;padding:10px;">${progressoTotalHtml}</td>
        </tr>
    `;
    tbody.innerHTML += trTotal;
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
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#6B7280;padding:30px;">Nenhum operador disponível</td></tr>';
        return;
    }

    // Ordena por faturamento
    todos.sort((a, b) => (b.faturamento || 0) - (a.faturamento || 0));

    tbody.innerHTML = todos.map(op => {
        const bancoCor = op.banco === 'SEMEAR' ? '#7e3d97' : '#10B981';
        const fotoHtml = op.imagem
            ? `<img src="${op.imagem}" alt="${op.login}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:2px solid ${bancoCor};">`
            : `<div style="width:32px;height:32px;border-radius:50%;background:${bancoCor};color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">${(op.login||'').replace(/[0-9]/g,'').substring(0,2).toUpperCase()}</div>`;

        const percMeta = op.perc_meta || 0;
        const corMeta = percMeta >= 100 ? '#10B981' : bancoCor;

        // Barra de progresso para a célula
        const progressoHtml = `
            <div class="table-progress-container" style="min-width:110px;">
                <div class="table-progress-bar">
                    <div class="table-progress-fill ${op.banco === 'SEMEAR' ? 'purple' : 'green'}" style="width: ${Math.min(percMeta, 100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color: ${corMeta};">${percMeta.toFixed(1)}%</span>
            </div>
        `;

        return `
            <tr>
                <td class="sticky-col-1" style="padding:8px 12px;text-align:center;">${fotoHtml}</td>
                <td class="sticky-col-2 sticky-col-name" style="padding:8px 12px;text-align:center;font-weight:600;color:var(--text-main);">${op.login || '-'}</td>
                <td style="padding:8px 12px;text-align:center;">
                    <span style="background:${bancoCor};color:white;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">${op.banco}</span>
                </td>
                <td style="padding:8px 12px;text-align:center;">${op.turno || '-'}</td>
                <td style="padding:8px 12px;text-align:center;font-size:11px;white-space:nowrap;">${op.tempo_casa || '-'}</td>
                <td style="padding:8px 12px;text-align:center;font-weight:700;">${formatarMoeda(op.faturamento || 0)}</td>
                <td style="padding:8px 12px;text-align:center;font-weight:700;">${op.quantidade || 0}</td>
                <td style="padding:8px 12px;text-align:center;">${progressoHtml}</td>
            </tr>
        `;
    }).join('');

    // Linha de Total consolidada
    const totalFat = todos.reduce((s, op) => s + (op.faturamento || 0), 0);
    const totalQtd = todos.reduce((s, op) => s + (op.quantidade || 0), 0);
    const totalMeta = todos.reduce((s, op) => s + (op.meta || 0), 0);
    const totalPerc = totalMeta > 0 ? (totalFat / totalMeta) * 100 : 0;

    const progressoTotalHtml = `
        <div class="table-progress-container" style="min-width:110px;">
            <div class="table-progress-bar">
                <div class="table-progress-fill purple" style="width: ${Math.min(totalPerc, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: var(--purple-main);">${totalPerc.toFixed(1)}%</span>
        </div>
    `;

    const trTotal = `
        <tr class="sticky-total-row">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:var(--purple-main);"><strong>TOTAL</strong></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:var(--purple-main);"></td>
            <td style="text-align:center;padding:10px;color:var(--purple-main);"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:var(--purple-main);font-weight:700;">${formatarMoeda(totalFat)}</td>
            <td style="text-align:center;padding:10px;color:var(--purple-main);font-weight:700;">${totalQtd}</td>
            <td style="text-align:center;padding:10px;">${progressoTotalHtml}</td>
        </tr>
    `;
    tbody.innerHTML += trTotal;
    
    // Salva a lista de operadores globalmente e atualiza os filtros
    todosOperadoresCadastrados = todos;
    window.todosOperadoresCadastrados = todos; // garante acesso via window.* (usado em dashboard_adm.js)
    atualizarFiltrosOperadoresAdm();
    
    // Se a aba de operadores estiver ativa, atualiza a visão individual/consolidada
    if (document.getElementById('page-operadores')?.classList.contains('active')) {
        selecionarOperadorPerfAdm();
    }
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
        operadores: 'Operadores',
        campanhas: 'Campanhas'
    };
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) pageTitle.textContent = titulos[pagina] || pagina;

    // Se estiver na aba Operadores ou Horários, oculta elementos do topo global
    const topFiltersBar = document.querySelector('.filters-bar.filters-adm');
    if (topFiltersBar) {
        if (pagina === 'horarios') {
            topFiltersBar.style.display = 'none';
        } else {
            topFiltersBar.style.display = 'flex';
        }
    }

    const topOperadorMultiselect = document.getElementById('multiselect-operador-adm');
    if (topOperadorMultiselect) {
        if (pagina === 'operadores') {
            topOperadorMultiselect.style.display = 'none';
        } else {
            topOperadorMultiselect.style.display = 'block';
        }
    }

    // Atualiza dados específicos de cada aba ao navegar
    if (pagina === 'pagamentos') {
        if (typeof carregarPagamentosAdm === 'function') {
            carregarPagamentosAdm();
        }
    } else if (pagina === 'operadores') {
        if (typeof carregarDadosAdm === 'function') {
            carregarDadosAdm();
        }
    } else if (pagina === 'horarios') {
        if (typeof carregarPontoAdm === 'function') {
            carregarPontoAdm();
        }
    }
}


function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ================================================================
// ERROR
// ================================================================

function showErrorAdm(mensagem) {
    console.error('❌', mensagem);
    alert(mensagem);
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
        let pos = idx === 0 ? '1°' : idx === 1 ? '2°' : idx === 2 ? '3°' : `${idx+1}°`;

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-2 sticky-col-name" style="text-align:center;padding:8px 10px;font-weight:600;">
                    <span style="margin-right:6px;font-size:13px;">${pos}</span>${op.login || '-'}
                    <br><span style="background:${bancoCor};color:white;padding:1px 8px;border-radius:10px;font-size:10px;font-weight:600;">${op.banco}</span>
                </td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;font-family:monospace;font-size:14px;">${op.tma || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:#0891b2;">${op.acionamentos || 0}</td>
                <td style="text-align:center;padding:8px 10px;">${op.clientes || 0}</td>
                <td style="text-align:center;padding:8px 10px;font-size:12px;">${op.reacionamento || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-family:monospace;">${op.tempo_falado || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;color:var(--text-muted);">${_fmtAcion(op.primeiro_acionamento)}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;color:var(--text-muted);">${_fmtAcion(op.ultimo_acionamento)}</td>
            </tr>
        `;
    }).join('');

    // Linha de totais
    const totalRow = `
        <tr style="background:#e0f2fe;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;"></td>
            <td class="sticky-col-2" style="text-align:center;padding:10px;color:#0369a1;"><strong>TOTAL</strong></td>
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

// Override navegar para carregar TMA quando ir para Operadores ou Pagamentos
(function() {
    const _navegar = window.navegar;
    window.navegar = function(pagina) {
        _navegar(pagina);
        if (pagina === 'operadores') {
            // Sincroniza o filtro de mês/ano da aba com o filtro principal atual
            const mesPrincipal = document.getElementById('filtro-mes-adm')?.value;
            const anoPrincipal = document.getElementById('filtro-ano-adm')?.value;
            const filtroMesOp = document.getElementById('filtro-mes-adm-op');
            const filtroAnoOp = document.getElementById('filtro-ano-adm-op');
            if (filtroMesOp && mesPrincipal) filtroMesOp.value = mesPrincipal;
            if (filtroAnoOp && anoPrincipal) filtroAnoOp.value = anoPrincipal;

            // Seleciona consolidado SEMEAR por padrão ao entrar na aba
            const sel = document.getElementById('filtro-operador-perf-adm');
            if (sel) {
                sel.value = "CONSOLIDADO_SEMEAR";
                selecionarOperadorPerfAdm();
            }

            // Renderiza o pivot Operador × Mês imediatamente (SEMEAR por padrão)
            // O card agora é permanente (display:block) — só precisa preencher os dados
            if (typeof renderizarMesOperadorAdm === 'function') {
                renderizarMesOperadorAdm(window._pivotSemear || [], 'SEMEAR');
                // Reseta botões do pivot para SEMEAR ativo
                const btnS = document.getElementById('btn-pivot-semear');
                const btnA = document.getElementById('btn-pivot-agoracred');
                const head = document.getElementById('thead-mes-operador-adm');
                const tit  = document.getElementById('titulo-mes-operador-adm');
                if (btnS) { btnS.style.background = '#7E3E9A'; btnS.style.color = 'white'; }
                if (btnA) { btnA.style.background = 'transparent'; btnA.style.color = '#10b981'; }
                if (head) head.style.background = '#7E3E9A';
                if (tit)  tit.style.color = '#7E3E9A';
            }
        } else if (pagina === 'pagamentos') {
            // Sincroniza o mês/ano da aba de pagamentos com o filtro principal ANTES de carregar
            const mesPrincipal = document.getElementById('filtro-mes-adm')?.value || getMesAtual();
            const anoPrincipal = document.getElementById('filtro-ano-adm')?.value || getAnoAtual();
            const filtroPagMes = document.getElementById('filtro-pag-mes-adm');
            const filtroPagAno = document.getElementById('filtro-pag-ano-adm');
            if (filtroPagMes) filtroPagMes.value = mesPrincipal;
            if (filtroPagAno) filtroPagAno.value = anoPrincipal;
            carregarPagamentosAdm();
        }
    };
})();

// ================================================================
// FILTRO DE PERÍODO NA ABA OPERADORES (mês/ano)
// ================================================================

async function filtrarPeriodoOperadoresAdm() {
    const mes = document.getElementById('filtro-mes-adm-op')?.value;
    const ano = document.getElementById('filtro-ano-adm-op')?.value;

    // Mantém os filtros principais sincronizados
    const filtroMesPrincipal = document.getElementById('filtro-mes-adm');
    const filtroAnoPrincipal = document.getElementById('filtro-ano-adm');
    if (filtroMesPrincipal && mes) filtroMesPrincipal.value = mes;
    if (filtroAnoPrincipal && ano) filtroAnoPrincipal.value = ano;

    // Sincroniza a atividade selecionada na aba com o dashboard principal
    const ativOp = document.getElementById('filtro-atividade-op-adm')?.value;
    const ativPrincipal = document.getElementById('filtro-atividade-adm');
    if (ativPrincipal && ativOp) ativPrincipal.value = ativOp;

    await carregarDadosAdm();

    // Se tiver um operador individual selecionado, recarrega a performance dele no novo período
    const selOperador = document.getElementById('filtro-operador-perf-adm');
    if (selOperador && selOperador.value) {
        await selecionarOperadorPerfAdm();
    }
}
window.filtrarPeriodoOperadoresAdm = filtrarPeriodoOperadoresAdm;

// ================================================================
// FUNÇÕES DE MONITORAMENTO INDIVIDUAL E CONSOLIDADO DE OPERADORES (ADM)
// ================================================================

let _admOpSelecionadoData = null;
let chartMensalOpAdm = null;

function obterDadosConsolidadosBanco(banco) {
    const dadosBanco = banco === 'SEMEAR' ? dadosAdmCompletos.semear : dadosAdmCompletos.agoracred;
    if (!dadosBanco) return null;

    const faturamento = dadosBanco.faturamento || 0;
    const meta = dadosBanco.meta || 0;
    const anterior = dadosBanco.anterior || 0;

    // Pega dias trabalhados e total de dias do mês do primeiro operador válido no ranking
    const opValido = dadosBanco.operadores && dadosBanco.operadores[0];
    const diasTrabalhados = opValido ? (opValido.dias_trabalhados || 1) : 1;
    const totalDiasUteis = opValido ? (opValido.total_dias_uteis || 1) : 1;
    const diasRestantes = Math.max(0, totalDiasUteis - diasTrabalhados);

    const feitoDiario = faturamento / diasTrabalhados;
    const atingidoMeta = meta > 0 ? (faturamento / meta) * 100 : 0;
    const projecao = diasTrabalhados > 0 ? (faturamento / diasTrabalhados * totalDiasUteis) : 0;

    const perf = {
        login: `GRUPO ${banco}`,
        turno: 'GERAL',
        quantidade: dadosBanco.operacoes || 0,
        faturamento: faturamento,
        feito_diario: feitoDiario,
        meta: meta,
        meta_diaria: totalDiasUteis > 0 ? (meta / totalDiasUteis) : 0,
        atingido_meta: atingidoMeta,
        falta_70: Math.max(0, (meta * 0.7) - faturamento),
        falta_80: Math.max(0, (meta * 0.8) - faturamento),
        falta_90: Math.max(0, (meta * 0.9) - faturamento),
        falta_100: Math.max(0, meta - faturamento),
        ranking: '—',
        projecao: projecao,
        projecao_percentual: meta > 0 ? (projecao / meta) * 100 : 0,
        dias_trabalhados: diasTrabalhados,
        total_dias_uteis: totalDiasUteis,
        dias_restantes: diasRestantes,
        ultima_baixa_banco: dadosBanco.ultima_baixa
    };

    // Meta diária consolidada do banco
    const metaDiaria = totalDiasUteis > 0 ? (meta / totalDiasUteis) : 0;

    const DIAS_ABREV = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];
    let duCount = 0;

    // Mapeia a evolução diária (faturamento diário consolidado)
    const performanceDiaria = (dadosBanco.evolucao || []).map(ev => {
        const dtStr = ev.data || ev.dtPgto || '';
        let dataFormatada = '—';
        let diaUtilStr = '—';
        let diaNum = 0;

        if (dtStr.includes('-')) {
            const parts = dtStr.split('-');
            if (parts.length === 3) {
                const a = parseInt(parts[0], 10);
                const m = parseInt(parts[1], 10);
                const d = parseInt(parts[2], 10);
                diaNum = d;
                const dtObj = new Date(a, m - 1, d);
                const wday = dtObj.getDay();
                dataFormatada = `${String(d).padStart(2, '0')} - ${DIAS_ABREV[wday]}`;
                if (wday >= 1 && wday <= 5) {
                    duCount++;
                    diaUtilStr = `${duCount}º DU`;
                } else {
                    diaUtilStr = 'Feriado/Fim de semana';
                }
            }
        }

        const realizadoVal = ev.total || 0;
        const bateu = realizadoVal >= metaDiaria ? '✅ Sim' : '❌ Não';

        return {
            dia: diaNum,
            data: dtStr,
            dtPgto: dtStr,
            data_formatada: dataFormatada,
            dia_util: diaUtilStr,
            quantidade: ev.quantidade || 0,
            realizado: formatarMoeda(realizadoVal),
            meta_diaria: formatarMoeda(metaDiaria),
            meta_batida: bateu
        };
    });

    const ultimosPagamentos = (dadosBanco.evolucao || []).map(ev => ({
        dtPgto: ev.data,
        valorTotal: ev.total,
        quantidade: ev.quantidade || 0
    }));

    // Usa o histórico real de 12 meses retornado pela API (resultado_mes_a_mes)
    // O backend (admin_service.py > montar_historico_mensal_banco) já calcula Janeiro a Dezembro
    const resultadoMesAMes = dadosBanco.resultado_mes_a_mes || [
        {
            mes: 0,
            mes_nome: 'Mês Anterior',
            contratos: dadosBanco.operacoes_anterior || 0,
            faturamento: anterior,
            meta: meta,
            perc_meta: meta > 0 ? (anterior / meta) * 100 : 0,
        },
        {
            mes: 0,
            mes_nome: 'Mês Atual',
            contratos: dadosBanco.operacoes || 0,
            faturamento: faturamento,
            meta: meta,
            perc_meta: atingidoMeta,
        }
    ];

    return {
        performance: perf,
        performance_diaria: performanceDiaria,
        ultimos_pagamentos: ultimosPagamentos,
        resultado_mes_a_mes: resultadoMesAMes,
        indicadores_anterior: {
            faturamento_total: anterior
        }
    };
}

function atualizarFiltrosOperadoresAdm() {
    const banco = document.getElementById('filtro-banco-adm')?.value || 'TODOS';
    const atividade = document.getElementById('filtro-atividade-adm')?.value || 'ATIVO';
    const sel = document.getElementById('filtro-operador-perf-adm');
    if (!sel) return;

    // Salva o valor atualmente selecionado
    const valAtual = sel.value;

    // Limpa e repovoa com consolidados no topo + operadores individuais abaixo
    sel.innerHTML = '';

    if (banco === 'TODOS' || banco === 'SEMEAR') {
        const optSem = document.createElement('option');
        optSem.value = 'CONSOLIDADO_SEMEAR';
        optSem.textContent = '── Visão Geral Consolidada — SEMEAR ──';
        sel.appendChild(optSem);
    }
    if (banco === 'TODOS' || banco === 'AGORACRED') {
        const optAgo = document.createElement('option');
        optAgo.value = 'CONSOLIDADO_AGORACRED';
        optAgo.textContent = '── Visão Geral Consolidada — AGORACRED ──';
        sel.appendChild(optAgo);
    }

    const optTabela = document.createElement('option');
    optTabela.value = 'LISTA_OPERADORES';
    optTabela.textContent = '── Lista Geral (Tabela) ──';
    sel.appendChild(optTabela);

    // Separador visual
    const sep = document.createElement('option');
    sep.disabled = true;
    sep.textContent = '─────────────────────';
    sel.appendChild(sep);

    // Filtra e popula operadores individuais
    const operadoresFiltrados = (window.todosOperadoresCadastrados || []).filter(op => {
        const matchBanco = banco === 'TODOS' || op.banco === banco;
        const matchAtiv = atividade === 'TODOS' || (op.atividade && op.atividade.toUpperCase() === 'ATIVO');
        return matchBanco && matchAtiv;
    });

    const loginsUnicos = new Set();
    operadoresFiltrados.forEach(op => {
        if (op.login && !loginsUnicos.has(op.login)) {
            loginsUnicos.add(op.login);
            const opt = document.createElement('option');
            opt.value = op.login;
            opt.dataset.banco = op.banco;
            opt.textContent = `${op.login}${op.banco ? ' (' + op.banco + ')' : ''}`;
            sel.appendChild(opt);
        }
    });

    // Recupera valor se ainda existir na lista de opções
    if (Array.from(sel.options).some(opt => opt.value === valAtual)) {
        sel.value = valAtual;
    } else {
        sel.value = banco === 'AGORACRED' ? 'CONSOLIDADO_AGORACRED' : 'CONSOLIDADO_SEMEAR';
    }

    // Renderiza também as opções do dropdown customizado com pesquisa
    renderizarOptionsOperadoresPerfCustom();

    console.log(`[ADM FILTROS] Operadores atualizados. Banco: ${banco}, Total: ${operadoresFiltrados.length}`);
}

function renderizarOptionsOperadoresPerfCustom() {
    const container = document.getElementById('options-operadores-perf-container');
    const sel = document.getElementById('filtro-operador-perf-adm');
    const labelHeader = document.getElementById('label-operador-perf-selecionado');
    if (!container || !sel) return;

    const valAtual = sel.value;
    const banco = document.getElementById('filtro-banco-adm')?.value || 'TODOS';
    const atividade = document.getElementById('filtro-atividade-adm')?.value || 'ATIVO';

    let html = '';

    // Consolidados
    if (banco === 'TODOS' || banco === 'SEMEAR') {
        const isSel = valAtual === 'CONSOLIDADO_SEMEAR';
        if (isSel && labelHeader) labelHeader.textContent = 'Visão Geral Consolidada — SEMEAR';
        html += `
            <div class="perf-op-item" data-value="CONSOLIDADO_SEMEAR" onclick="selecionarOperadorPerfCustom('CONSOLIDADO_SEMEAR', 'Visão Geral Consolidada — SEMEAR')" style="padding:8px 12px;font-size:12px;font-weight:700;color:var(--purple-main);cursor:pointer;border-radius:6px;display:flex;align-items:center;justify-content:space-between;background:${isSel ? '#f3e8ff' : 'transparent'};margin-bottom:2px;" onmouseover="this.style.background='#f3e8ff'" onmouseout="this.style.background='${isSel ? '#f3e8ff' : 'transparent'}'">
                <span><i class="fas fa-building" style="margin-right:6px;color:var(--purple-main);"></i> Visão Geral Consolidada — SEMEAR</span>
                <span style="font-size:9px;background:#7e3d9720;color:#7e3d97;padding:1px 6px;border-radius:10px;font-weight:700;">SEMEAR</span>
            </div>
        `;
    }

    if (banco === 'TODOS' || banco === 'AGORACRED') {
        const isSel = valAtual === 'CONSOLIDADO_AGORACRED';
        if (isSel && labelHeader) labelHeader.textContent = 'Visão Geral Consolidada — AGORACRED';
        html += `
            <div class="perf-op-item" data-value="CONSOLIDADO_AGORACRED" onclick="selecionarOperadorPerfCustom('CONSOLIDADO_AGORACRED', 'Visão Geral Consolidada — AGORACRED')" style="padding:8px 12px;font-size:12px;font-weight:700;color:#047857;cursor:pointer;border-radius:6px;display:flex;align-items:center;justify-content:space-between;background:${isSel ? '#d1fae5' : 'transparent'};margin-bottom:2px;" onmouseover="this.style.background='#d1fae5'" onmouseout="this.style.background='${isSel ? '#d1fae5' : 'transparent'}'">
                <span><i class="fas fa-building" style="margin-right:6px;color:#10B981;"></i> Visão Geral Consolidada — AGORACRED</span>
                <span style="font-size:9px;background:#10B98120;color:#10B981;padding:1px 6px;border-radius:10px;font-weight:700;">AGORACRED</span>
            </div>
        `;
    }

    const isSelTab = valAtual === 'LISTA_OPERADORES';
    if (isSelTab && labelHeader) labelHeader.textContent = 'Lista Geral de Operadores (Tabela)';
    html += `
        <div class="perf-op-item" data-value="LISTA_OPERADORES" onclick="selecionarOperadorPerfCustom('LISTA_OPERADORES', 'Lista Geral de Operadores (Tabela)')" style="padding:8px 12px;font-size:12px;font-weight:700;color:#374151;cursor:pointer;border-radius:6px;display:flex;align-items:center;justify-content:space-between;background:${isSelTab ? '#e5e7eb' : 'transparent'};margin-bottom:6px;border-bottom:1px solid #f3f4f6;" onmouseover="this.style.background='#e5e7eb'" onmouseout="this.style.background='${isSelTab ? '#e5e7eb' : 'transparent'}'">
            <span><i class="fas fa-table" style="margin-right:6px;color:#6b7280;"></i> Lista Geral de Operadores (Tabela)</span>
            <span style="font-size:9px;background:#6b728020;color:#6b7280;padding:1px 6px;border-radius:10px;font-weight:700;">TABELA</span>
        </div>
    `;

    // Operadores Individuais
    const operadoresFiltrados = (window.todosOperadoresCadastrados || []).filter(op => {
        const matchBanco = banco === 'TODOS' || op.banco === banco;
        const matchAtiv = atividade === 'TODOS' || (op.atividade && op.atividade.toUpperCase() === 'ATIVO');
        return matchBanco && matchAtiv;
    });

    const loginsUnicos = new Set();
    operadoresFiltrados.forEach(op => {
        if (op.login && !loginsUnicos.has(op.login)) {
            loginsUnicos.add(op.login);
            const isSelOp = valAtual === op.login;
            if (isSelOp && labelHeader) labelHeader.textContent = op.login;
            const corBanco = op.banco === 'SEMEAR' ? '#7e3d97' : '#10b981';
            html += `
                <div class="perf-op-item" data-value="${op.login}" onclick="selecionarOperadorPerfCustom('${op.login}', '${op.login}')" style="padding:6px 10px;font-size:12px;font-weight:600;color:#374151;cursor:pointer;border-radius:6px;display:flex;align-items:center;justify-content:space-between;background:${isSelOp ? '#f3f4f6' : 'transparent'};margin-bottom:2px;" onmouseover="this.style.background='#f3f4f6'" onmouseout="this.style.background='${isSelOp ? '#f3f4f6' : 'transparent'}'">
                    <span style="display:flex;align-items:center;gap:6px;"><i class="fas fa-user-circle" style="color:${corBanco};"></i> <span>${op.login}</span></span>
                    <span style="font-size:9px;background:${corBanco}20;color:${corBanco};padding:1px 6px;border-radius:10px;font-weight:600;">${op.banco || ''}</span>
                </div>
            `;
        }
    });

    container.innerHTML = html;
}

function filtrarOperadoresPerfDropdown(termo) {
    const termoLower = (termo || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const container = document.getElementById('options-operadores-perf-container');
    if (!container) return;
    const items = container.querySelectorAll('.perf-op-item');
    items.forEach(item => {
        const text = item.textContent || '';
        const textLower = text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        if (textLower.includes(termoLower)) {
            item.style.setProperty('display', 'flex', 'important');
        } else {
            item.style.setProperty('display', 'none', 'important');
        }
    });
}

function selecionarOperadorPerfCustom(val, label) {
    const sel = document.getElementById('filtro-operador-perf-adm');
    const labelHeader = document.getElementById('label-operador-perf-selecionado');
    const dropdown = document.getElementById('dropdown-perf-operadores-content');

    if (sel) {
        sel.value = val;
    }
    if (labelHeader) {
        labelHeader.textContent = label;
    }
    if (dropdown) {
        dropdown.style.display = 'none';
    }

    renderizarOptionsOperadoresPerfCustom();

    if (typeof selecionarOperadorPerfAdm === 'function') {
        selecionarOperadorPerfAdm();
    }
}

window.renderizarOptionsOperadoresPerfCustom = renderizarOptionsOperadoresPerfCustom;
window.filtrarOperadoresPerfDropdown          = filtrarOperadoresPerfDropdown;
window.selecionarOperadorPerfCustom           = selecionarOperadorPerfCustom;


function filtrarBancoOperadoresAdm() {
    // Ao mudar o banco na aba operadores, atualiza a lista de operadores disponíveis
    atualizarFiltrosOperadoresAdm();
    // E aciona a seleção do novo consolidado padrão correspondente
    selecionarOperadorPerfAdm();
}

function onBuscaOperadorAdm(valor) {
    const sel = document.getElementById('filtro-operador-perf-adm');
    if (!sel) return;

    if (!valor || valor.trim() === '') return;

    // Exige match exato para evitar disparar a busca a cada letra digitada
    const valorUpper = valor.trim().toUpperCase();
    const optMatch = Array.from(sel.options).find(opt =>
        opt.value.toUpperCase() === valorUpper
    );

    if (optMatch) {
        sel.value = optMatch.value;
        selecionarOperadorPerfAdm();
        document.getElementById('busca-operador-perf-adm')?.blur();
    }
}

function voltarConsolidadoAdm() {
    const sel = document.getElementById('filtro-operador-perf-adm');
    const buscaInput = document.getElementById('busca-operador-perf-adm');
    const banco = document.getElementById('filtro-banco-adm')?.value || 'TODOS';

    if (buscaInput) buscaInput.value = '';
    if (sel) {
        sel.value = banco === 'AGORACRED' ? 'CONSOLIDADO_AGORACRED' : 'CONSOLIDADO_SEMEAR';
    }

    const banner = document.getElementById('banner-operador-selecionado-adm');
    if (banner) banner.style.display = 'none';

    selecionarOperadorPerfAdm();
}

// Expõe para eventos globais
window.filtrarBancoOperadoresAdm = filtrarBancoOperadoresAdm;
window.onBuscaOperadorAdm = onBuscaOperadorAdm;
window.voltarConsolidadoAdm = voltarConsolidadoAdm;

async function selecionarOperadorPerfAdm() {
    const sel = document.getElementById('filtro-operador-perf-adm');
    const painelGeral = document.getElementById('painel-geral-operadores-adm');
    const painelIndiv = document.getElementById('painel-perf-individual-adm');
    const banner = document.getElementById('banner-operador-selecionado-adm');
    
    if (!sel || !painelGeral || !painelIndiv) return;
    
    const login = sel.value;
    
    if (login === 'LISTA_OPERADORES') {
        // Mostra a lista em formato de tabela
        painelGeral.style.display = 'block';
        painelIndiv.style.display = 'none';
        if (banner) banner.style.display = 'none';
        
        // Renderiza o pivot Mês × Operador (usa banco atual selecionado no filtro)
        const bancoPivot = document.getElementById('filtro-banco-adm')?.value || 'SEMEAR';
        if (typeof renderizarMesOperadorAdm === 'function') {
            if (bancoPivot === 'AGORACRED') {
                renderizarMesOperadorAdm(window._pivotAgoracred || [], 'AGORACRED');
            } else {
                renderizarMesOperadorAdm(window._pivotSemear || [], 'SEMEAR');
            }
        }
        
        // Se for lista geral, o select global do topo volta a ser TODOS
        const selGlobal = document.getElementById('filtro-operador-adm');
        if (selGlobal && selGlobal.value !== 'TODOS') {
            selGlobal.value = 'TODOS';
            carregarDadosAdm();
        }
        return;
    }
    
    // Se for consolidado SEMEAR ou consolidado AGORACRED
    if (login === 'CONSOLIDADO_SEMEAR' || login === 'CONSOLIDADO_AGORACRED') {
        painelGeral.style.display = 'none';
        painelIndiv.style.display = 'block';
        if (banner) banner.style.display = 'none';
        
        const banco = login === 'CONSOLIDADO_SEMEAR' ? 'SEMEAR' : 'AGORACRED';
        const mes = document.getElementById('filtro-mes-adm')?.value || getMesAtual();
        const ano = document.getElementById('filtro-ano-adm')?.value || getAnoAtual();
        
        // Define contexto para Visão Periódica do consolidado
        const loginConsolidado = login;
        window._admOpAtual    = loginConsolidado;
        window._admBancoAtual = banco;

        const dadosConsolidados = obterDadosConsolidadosBanco(banco);
        if (dadosConsolidados) {
            renderizarMinhaPerformanceOpAdm(dadosConsolidados, mes, ano);
        }

        // Exibe e carrega Visão Periódica para o consolidado
        const secaoPeriodica = document.getElementById('secao-visao-periodica-adm');
        if (secaoPeriodica) secaoPeriodica.style.display = 'block';
        if (typeof carregarVisaoPeriodicaAdm === 'function') {
            const btnDefault = document.querySelector('.btn-periodo-adm[data-meses="1"]');
            if (btnDefault) {
                document.querySelectorAll('.btn-periodo-adm').forEach(b => {
                    b.style.background = 'transparent';
                    b.style.color      = 'var(--purple-main)';
                });
                btnDefault.style.background = 'var(--purple-main)';
                btnDefault.style.color      = 'white';
            }
            // Para consolidado usa login fictício mapeado para o banco
            const loginApi = banco === 'SEMEAR' ? 'CONSOLIDADO_SEMEAR' : 'CONSOLIDADO_AGORACRED';
            carregarVisaoPeriodicaAdm(loginApi, banco, 1);
        }
        
        // Se consolidado, o select global do topo volta a ser TODOS
        const selGlobal = document.getElementById('filtro-operador-adm');
        if (selGlobal && selGlobal.value !== 'TODOS') {
            selGlobal.value = 'TODOS';
            carregarDadosAdm();
        }
        return;
    }
    
    // Oculta lista geral e mostra dashboard individual do operador
    painelGeral.style.display = 'none';
    painelIndiv.style.display = 'block';
    
    const optionSelected = sel.options[sel.selectedIndex];
    const banco = optionSelected?.dataset?.banco || 'SEMEAR';
    const mes = parseInt(document.getElementById('filtro-mes-adm')?.value || getMesAtual(), 10);
    const ano = parseInt(document.getElementById('filtro-ano-adm')?.value || getAnoAtual(), 10);
    
    const tbodyDiario = document.getElementById('tabela-recebimento-diario-adm-op');
    if (tbodyDiario) {
        tbodyDiario.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;"><i class="fas fa-spinner fa-spin"></i> Carregando dados do operador...</td></tr>';
    }
    
    const faixa = document.getElementById('filtro-faixa-adm')?.value || 'todas';
    try {
        const response = await fetch(`/api/resumo/${login}?mes=${mes}&ano=${ano}&faixa=${encodeURIComponent(faixa)}`);
        const data = await response.json();
        
        if (data.success) {
            const resumo = data.data;
            const perf = resumo.performance || {};
            const diarios = resumo.performance_diaria || [];
            const operadorInfo = resumo.operador || {};
            
            _admOpSelecionadoData = {
                performance: perf,
                performance_diaria: diarios,
                ultimos_pagamentos: resumo.ultimos_pagamentos || [],
                resultado_mes_a_mes: resumo.resultado_mes_a_mes || [],
                indicadores_anterior: resumo.indicadores_anterior || {},
                imagem: operadorInfo.imagem || perf.imagem || '',
                banco: operadorInfo.banco || banco,
                tempo_casa: operadorInfo.tempo_casa || resumo.tempo_casa || '',
                tma: resumo.tma || {}
            };

            // Salva login e banco para uso na Visão Periódica
            window._admOpAtual    = login;
            window._admBancoAtual = banco;

            renderizarMinhaPerformanceOpAdm(_admOpSelecionadoData, mes, ano);

            // Carrega Visão Periódica automaticamente com padrão de 1 mês
            if (typeof carregarVisaoPeriodicaAdm === 'function') {
                // Atualiza botões de período para refletir seleção inicial
                const btnDefault = document.querySelector('.btn-periodo-adm[data-meses="1"]');
                if (btnDefault) {
                    document.querySelectorAll('.btn-periodo-adm').forEach(b => {
                        b.style.background = 'transparent';
                        b.style.color      = 'var(--purple-main)';
                    });
                    btnDefault.style.background = 'var(--purple-main)';
                    btnDefault.style.color      = 'white';
                }
                carregarVisaoPeriodicaAdm(login, banco, 1);
            }

            // Exibe e atualiza o banner visual informativo
            if (banner) {
                const bannerName = document.getElementById('banner-op-nome');
                const bannerInfo = document.getElementById('banner-op-info');
                const bannerImg = document.getElementById('banner-op-avatar-img');
                const bannerTxt = document.getElementById('banner-op-avatar-txt');

                if (bannerName) bannerName.textContent = login;
                if (bannerInfo) {
                    bannerInfo.textContent = `Banco: ${banco} | Turno: ${perf.turno || '-'} | Tempo de casa: ${_admOpSelecionadoData.tempo_casa || 'não disponível'}`;
                }

                if (_admOpSelecionadoData.imagem) {
                    if (bannerImg) {
                        bannerImg.src = _admOpSelecionadoData.imagem;
                        bannerImg.style.display = 'block';
                    }
                    if (bannerTxt) bannerTxt.style.display = 'none';
                } else {
                    if (bannerTxt) {
                        bannerTxt.textContent = login.replace(/[0-9]/g, '').substring(0, 2).toUpperCase() || 'OP';
                        bannerTxt.style.display = 'flex';
                    }
                    if (bannerImg) bannerImg.style.display = 'none';
                }
                banner.style.display = 'flex';
            }
        } else {
            console.error('[ADM PERFORMANCE]', data.message);
            if (tbodyDiario) {
                tbodyDiario.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#dc2626;padding:20px;">Erro ao carregar dados: ${data.message}</td></tr>`;
            }
        }
    } catch (error) {
        console.error('[ADM PERFORMANCE]', error);
        if (tbodyDiario) {
            tbodyDiario.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#dc2626;padding:20px;">Erro de conexão ao carregar dados.</td></tr>';
        }
    }
}

function renderizarMinhaPerformanceOpAdm(dadosPerformance, mes, ano) {
    if (!dadosPerformance) return;

    const perf = dadosPerformance.performance || {};
    const diarios = dadosPerformance.performance_diaria || [];

    // --- 0. ATUALIZA O HEADER DO OPERADOR (Avatar + Nome + Banco) ---
    const avatarImg = document.getElementById('adm-op-avatar-img');
    const avatarIniciais = document.getElementById('adm-op-avatar-iniciais');
    const nomeEl = document.getElementById('adm-op-nome');
    const bancoEl = document.getElementById('adm-op-banco');
    const tempoCasaEl = document.getElementById('adm-op-tempo-casa');

    const login = perf.login || '—';
    const banco = dadosPerformance.banco || perf.banco || '';
    const imagem = dadosPerformance.imagem || perf.imagem || '';
    const tempoCasa = dadosPerformance.tempo_casa || perf.tempo_casa || '';

    if (nomeEl) nomeEl.textContent = login;
    if (bancoEl) bancoEl.textContent = banco || 'SEMEAR / AGORACRED';
    if (tempoCasaEl) tempoCasaEl.textContent = tempoCasa ? `Tempo de casa: ${tempoCasa}` : '';

    if (avatarImg && avatarIniciais) {
        if (imagem) {
            avatarImg.src = imagem;
            avatarImg.style.display = 'block';
            avatarIniciais.style.display = 'none';
        } else {
            // Sem foto: usa iniciais ou ícone de grupo para consolidado
            const isConsolidado = login.startsWith('GRUPO');
            if (isConsolidado) {
                avatarIniciais.innerHTML = '<i class="fas fa-users" style="font-size:28px;"></i>';
            } else {
                const iniciais = login.replace(/[0-9]/g, '').slice(0, 2).toUpperCase() || '??';
                avatarIniciais.textContent = iniciais;
            }
            avatarImg.style.display = 'none';
            avatarIniciais.style.display = 'flex';
        }
    }



    // --- 1. RENDERIZAR PERFORMANCE NA ABA DE PERFORMANCE ---
    const bannerUltimaBaixa = document.getElementById('banner-ultima-baixa-adm-aba');
    const txtUltimaBaixa = document.getElementById('txt-ultima-baixa-adm-aba');
    
    if (bannerUltimaBaixa && txtUltimaBaixa && perf.ultima_baixa_banco) {
        let dataFmt = perf.ultima_baixa_banco;
        if (dataFmt.includes('-')) {
            const p = dataFmt.split('-');
            dataFmt = `${p[2].substring(0,2)}/${p[1]}/${p[0]}`;
        }
        const duCalculado = typeof calcularDUdaData === 'function' ? calcularDUdaData(dataFmt) : '';
        const tagDu = duCalculado ? ` <span style="background:rgba(255,255,255,0.7);padding:2px 8px;border-radius:6px;font-size:12px;font-weight:700;margin-left:6px;border:1px solid currentColor;">${duCalculado}</span>` : '';
        
        const dTrabalhados = perf.dias_trabalhados || 0;
        const dTotal = perf.total_dias_uteis || 0;
        const dRestantes = Math.max(0, dTotal - dTrabalhados);
        
        const extrasHtml = `
        <div style="margin-top:6px;font-size:12.5px;font-weight:600;display:flex;gap:12px;color:var(--text-main);align-items:center;flex-wrap:wrap;">
            <span><i class="fas fa-calendar-check" style="margin-right:4px;color:var(--purple-main);opacity:0.8;"></i>Dias úteis trabalhados: ${dTrabalhados}</span>
            <span style="color:#cbd5e1;">|</span>
            <span><i class="fas fa-hourglass-half" style="margin-right:4px;color:var(--purple-main);opacity:0.8;"></i>Dias úteis restantes: ${dRestantes}</span>
            <span style="color:#cbd5e1;">|</span>
            <span><i class="fas fa-calendar-alt" style="margin-right:4px;color:var(--purple-main);opacity:0.8;"></i>Total de dias úteis no mês: ${dTotal}</span>
        </div>`;
        
        txtUltimaBaixa.style.display = 'block';
        txtUltimaBaixa.innerHTML = `
        <div style="display:flex;flex-direction:column;">
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                <strong style="font-size:14px;color:var(--text-main);">Baixas até ${dataFmt}</strong>${tagDu} 
                <span style="font-size:11.5px;color:var(--text-muted);margin-left:4px;font-weight:500;">(Feito/Dia e projeção calculados até esta data de baixas do banco)</span>
            </div>
            ${extrasHtml}
        </div>`;
        
        bannerUltimaBaixa.style.display = 'flex';
        bannerUltimaBaixa.style.alignItems = 'flex-start';
        
        const isAgoracred = banco === 'AGORACRED';
        bannerUltimaBaixa.style.background = isAgoracred ? 'linear-gradient(90deg,#10b98115,#34d39905)' : 'linear-gradient(90deg,#7e3d9715,#a855f705)';
        bannerUltimaBaixa.style.borderColor = isAgoracred ? '#10b98130' : '#a855f730';
        const iconeBanner = bannerUltimaBaixa.querySelector('i');
        if (iconeBanner) iconeBanner.style.color = isAgoracred ? '#10b981' : '#a855f7';
    } else if (bannerUltimaBaixa) {
        bannerUltimaBaixa.style.display = 'none';
    }

    const tbodyPerf = document.getElementById('tabela-performance-operador-adm-aba');
    if (tbodyPerf) {
        const theadPerf = tbodyPerf.previousElementSibling;
        if (theadPerf) {
            theadPerf.style.backgroundColor = (banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
        }
        const iniciaisOpPerf = login.replace(/[0-9]/g, '').slice(0, 2).toUpperCase() || '??';
        const fotoHtmlPerf = imagem
            ? `<img src="${imagem}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;margin:0 auto;display:block;">`
            : (login.startsWith('GRUPO') 
                ? `<div style="width:32px;height:32px;border-radius:50%;background:var(--purple-main);color:white;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;margin:0 auto;"><i class="fas fa-users"></i></div>`
                : `<div style="width:32px;height:32px;border-radius:50%;background:var(--purple-main);color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;margin:0 auto;">${iniciaisOpPerf}</div>`);

        const metaDiariaCalculada = perf.meta_diaria || (perf.total_dias_uteis > 0 ? (perf.meta / perf.total_dias_uteis) : 0);
        const atingido = perf.atingido_meta || 0;
        const projPercentual = perf.projecao_percentual || (perf.meta > 0 ? (perf.projecao / perf.meta) * 100 : 0);

        tbodyPerf.innerHTML = `
            <tr>
                <td style="text-align:center;">${fotoHtmlPerf}</td>
                <td style="text-align:center;font-weight:600;color:var(--purple-main);">${login}</td>
                <td style="text-align:center;">${perf.turno || '-'}</td>
                <td style="text-align:center;font-weight:700;color:var(--purple-main);">${perf.quantidade || 0}</td>
                <td style="text-align:center;font-weight:700;">${formatarMoeda(perf.faturamento || 0)}</td>
                <td style="text-align:center;">${formatarMoeda(perf.feito_diario || 0)}</td>
                <td style="text-align:center;font-weight:700;">${formatarMoeda(perf.meta || 0)}</td>
                <td style="text-align:center;">${formatarMoeda(metaDiariaCalculada)}</td>
                <td style="text-align:center;">${criarBarraProgresso(atingido)}</td>
                <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_70 || 0)}</td>
                <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_80 || 0)}</td>
                <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_90 || 0)}</td>
                <td style="text-align:center;color:#7c3aed;font-weight:700;">${formatarMoeda(perf.falta_100 || 0)}</td>
                <td style="text-align:center;font-weight:700;">${perf.ranking || '—'}</td>
                <td style="text-align:center;font-weight:700;color:#0891b2;">${formatarMoeda(perf.projecao || 0)}</td>
                <td style="text-align:center;">${criarBarraProgresso(projPercentual)}</td>
            </tr>
        `;
    }

    // --- 1b. MINI-CARD FAIXAS ≤360 / >360 (apenas SEMEAR) ---
    const faixasOp = dadosPerformance.faixas_operador || null;
    if (faixasOp && banco === 'SEMEAR') {
        const ate   = faixasOp.ate_360   || {};
        const acima = faixasOp.acima_360 || {};
        const cardHtml = `
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;">
            <div style="flex:1;min-width:180px;background:linear-gradient(135deg,#d1fae5,#a7f3d0);border-radius:12px;padding:14px 18px;border-left:5px solid #10b981;">
                <div style="font-size:10px;font-weight:700;color:#065f46;letter-spacing:.5px;margin-bottom:4px;">🟢 ATÉ 360 DIAS (META)</div>
                <div style="font-size:18px;font-weight:900;color:#065f46;">${formatarMoeda(ate.total || 0)}</div>
                <div style="font-size:11px;color:#047857;margin-top:3px;">${ate.qtd || 0} pgtos · ${ate.percentual || 0}% do total</div>
            </div>
            <div style="flex:1;min-width:180px;background:linear-gradient(135deg,#fee2e2,#fecaca);border-radius:12px;padding:14px 18px;border-left:5px solid #ef4444;">
                <div style="font-size:10px;font-weight:700;color:#991b1b;letter-spacing:.5px;margin-bottom:4px;">🔴 ACIMA DE 360 DIAS</div>
                <div style="font-size:18px;font-weight:900;color:#991b1b;">${formatarMoeda(acima.total || 0)}</div>
                <div style="font-size:11px;color:#b91c1c;margin-top:3px;">${acima.qtd || 0} pgtos · ${acima.percentual || 0}% do total</div>
            </div>
        </div>`;
        let miniCard = document.getElementById('mini-card-faixas-op-adm');
        if (!miniCard) {
            miniCard = document.createElement('div');
            miniCard.id = 'mini-card-faixas-op-adm';
            const diasBlock = document.getElementById('adm-op-dias-trab');
            if (diasBlock) diasBlock.closest('.card-full')?.before(miniCard);
        }
        miniCard.innerHTML = cardHtml;
        miniCard.style.display = 'block';
    } else {
        const mc = document.getElementById('mini-card-faixas-op-adm');
        if (mc) mc.style.display = 'none';
    }

    // --- 2. RESUMO DOS DIAS ---

    let diasComMeta = 0;
    let diasSemMeta = 0;
    diarios.forEach(d => {
        if (d.meta_batida && d.meta_batida.includes('Sim')) diasComMeta++;
        else if (d.meta_batida && d.meta_batida.includes('Não')) diasSemMeta++;
    });

    document.getElementById('adm-op-dias-trab').textContent = perf.dias_trabalhados || 0;
    document.getElementById('adm-op-dias-com-meta').textContent = diasComMeta;
    document.getElementById('adm-op-dias-sem-meta').textContent = diasSemMeta;
    const _diasRestCalc = Math.max(0, (perf.total_dias_uteis || 0) - (perf.dias_trabalhados || 0));
    document.getElementById('adm-op-dias-rest').textContent = (perf.dias_restantes != null) ? perf.dias_restantes : _diasRestCalc;
    document.getElementById('adm-op-total-dias').textContent = perf.total_dias_uteis || 0;


    // --- 3. RECEBIMENTO DIÁRIO ---
    const tbodyDiario = document.getElementById('tabela-recebimento-diario-adm-op');
    if (tbodyDiario) {
        const theadDiario = tbodyDiario.previousElementSibling;
        if (theadDiario) {
            theadDiario.style.backgroundColor = (banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
        }
        if (diarios.length === 0) {
            tbodyDiario.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#6B7280;padding:20px;">Nenhum faturamento registrado nos dias úteis.</td></tr>';
        } else {
            tbodyDiario.innerHTML = diarios.map((d) => {
                // Usa os campos já formatados pelo backend ou fallback estruturado
                const dataExib = d.data_formatada || d.data || d.dtPgto || '—';
                const duExib = d.dia_util || (d.dia ? `${d.dia}º DU` : '—');
                const qtd = d.quantidade ?? d.qtd ?? 0;
                const realizadoStr = d.realizado || 'R$ 0,00';
                const metaDiariaStr = d.meta_diaria || '—';
                const metaBatida = d.meta_batida || '❌ Não';

                return `
                    <tr>
                        <td style="text-align:center;font-weight:600;">${dataExib}</td>
                        <td style="text-align:center;">${duExib}</td>
                        <td style="text-align:center;">${qtd}</td>
                        <td style="text-align:center;font-weight:600;">${realizadoStr}</td>
                        <td style="text-align:center;">${metaDiariaStr}</td>
                        <td style="text-align:center;">
                            <span style="padding:2px 8px;border-radius:12px;font-weight:700;font-size:11px;background:${metaBatida.includes('Sim')?'#dcfce7':'#fee2e2'};color:${metaBatida.includes('Sim')?'#16a34a':'#dc2626'};"> ${metaBatida}</span>
                        </td>
                    </tr>
                `;
            }).join('');
        }
    }

    // --- 4. FATURAMENTO POR SEMANA ---
    renderizarSemanalOpAdm(dadosPerformance.ultimos_pagamentos || [], mes, banco);

    // --- 5. RESULTADO MÊS A MÊS ---
    const tbodyMesAPerf = document.getElementById('tabela-resultado-mes-a-mes-adm-op');
    if (tbodyMesAPerf && dadosPerformance.resultado_mes_a_mes) {
        const isAgora = banco === 'AGORACRED';
        const mainColor = isAgora ? 'var(--emerald)' : 'var(--purple-main)';
        const projHeaderColor = isAgora ? '#047857' : '#5b21b6';
        const projCellBg = isAgora ? '#d1fae5' : '#f3e8ff';
        const projMoneyColor = isAgora ? '#047857' : '#5b21b6';

        const theadMesAPerf = tbodyMesAPerf.previousElementSibling;
        if (theadMesAPerf) {
            theadMesAPerf.style.backgroundColor = mainColor;
            const thVal = document.getElementById('th-projecao-val-adm');
            const thPct = document.getElementById('th-projecao-pct-adm');
            if (thVal) thVal.style.backgroundColor = projHeaderColor;
            if (thPct) thPct.style.backgroundColor = projHeaderColor;
        }

        const listaHistorico = dadosPerformance.resultado_mes_a_mes;
        tbodyMesAPerf.innerHTML = listaHistorico.map((item, idx) => {
            // suporte aos campos do backend (mes_nome) e legado (mes)
            const nomeMes = item.mes_nome || (typeof item.mes === 'string' ? item.mes : String(item.mes));
            const contratos = item.contratos ?? item.quantidade ?? 0;
            const perc = typeof item.perc_meta === 'number' ? item.perc_meta : 0;
            const bateu = item.bateu ?? (perc >= 100 ? 'Sim' : 'Não');
            const bateuCor = bateu === 'Sim' ? '#16a34a' : '#dc2626';
            const bateuBg = bateu === 'Sim' ? '#dcfce7' : '#fee2e2';

            const proj = item.projecao || 0;
            const projPct = item.projecao_percentual || 0;
            const projCor = projPct >= 100 ? '#16a34a' : projPct >= 80 ? '#d97706' : '#dc2626';
            const projHtml = proj > 0
                ? `<span style="font-weight:700;color:${projMoneyColor};">${formatarMoeda(proj)}</span>`
                : '<span style="color:#9ca3af;">—</span>';
            const projPctHtml = proj > 0
                ? `<span style="font-weight:700;color:${projCor};">${projPct.toFixed(1)}%</span>`
                : '<span style="color:#9ca3af;">—</span>';

            return `
                <tr style="background:${idx % 2 === 0 ? '#fff' : '#f9fafb'}">
                    <td style="text-align:center;font-weight:600;">${nomeMes}</td>
                    <td style="text-align:center;">${contratos}</td>
                    <td style="text-align:center;font-weight:600;">${formatarMoeda(item.faturamento)}</td>
                    <td style="text-align:center;">${formatarMoeda(item.meta)}</td>
                    <td style="text-align:center;font-weight:600;">${perc.toFixed(1)}%</td>
                    <td style="text-align:center;">
                        <span style="background:${bateuBg};color:${bateuCor};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;">${bateu}</span>
                    </td>
                    <td style="text-align:center;background:${projCellBg};">${projHtml}</td>
                    <td style="text-align:center;background:${projCellBg};">${projPctHtml}</td>
                </tr>
            `;
        }).join('');
    }

    // --- 6. VARIAÇÃO VS MÊS ANTERIOR ---
    const divVar = document.getElementById('adm-op-variacao-periodo-detalhe');
    if (divVar) {
        const fatMes = perf.faturamento || 0;
        const fatAnt = (dadosPerformance.indicadores_anterior && dadosPerformance.indicadores_anterior.faturamento_total) || 0;
        const variacao = fatAnt > 0 ? ((fatMes - fatAnt) / fatAnt) * 100 : 0;
        const dif = fatMes - fatAnt;

        if (dif >= 0) {
            divVar.style.background = '#dcfce7';
            divVar.style.color = '#15803d';
            divVar.innerHTML = `<i class="fas fa-arrow-trend-up"></i> Variação de +${variacao.toFixed(1)}% (${formatarMoeda(dif)} a mais) em relação ao mês anterior.`;
        } else {
            divVar.style.background = '#fee2e2';
            divVar.style.color = '#b91c1c';
            divVar.innerHTML = `<i class="fas fa-arrow-trend-down"></i> Variação de ${variacao.toFixed(1)}% (${formatarMoeda(Math.abs(dif))} a menos) em relação ao mês anterior.`;
        }
    }

    // --- 6b. TABELA DE VARIAÇÃO DETALHADA ---
    renderizarVariacaoDetalhadaAdmOp(dadosPerformance.resultado_mes_a_mes || []);

    // --- 7. GRÁFICOS ---
    renderizarGraficoBarrasMensalOpAdm(dadosPerformance.resultado_mes_a_mes || [], banco);
}

function renderizarSemanalOpAdm(pagamentosRecentes, mes, banco) {
    const tbody = document.getElementById('tabela-faturamento-semanal-adm-op');
    if (!tbody) return;

    const theadSemanal = tbody.previousElementSibling;
    if (theadSemanal) {
        theadSemanal.style.backgroundColor = (banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
    }

    if (!pagamentosRecentes || pagamentosRecentes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#6B7280;padding:20px;">Sem pagamentos no período.</td></tr>';
        return;
    }

    const semanas = [
        { nome: 'Semana 1', inicio: 1, fim: 7, total: 0, qtd: 0 },
        { nome: 'Semana 2', inicio: 8, fim: 14, total: 0, qtd: 0 },
        { nome: 'Semana 3', inicio: 15, fim: 21, total: 0, qtd: 0 },
        { nome: 'Semana 4', inicio: 22, fim: 28, total: 0, qtd: 0 },
        { nome: 'Semana 5', inicio: 29, fim: 31, total: 0, qtd: 0 }
    ];

    pagamentosRecentes.forEach(p => {
        const dtStr = p.dtPgto || '';
        if (!dtStr.includes('-')) return;
        const dia = parseInt(dtStr.split('-')[2], 10);
        if (isNaN(dia)) return;

        for (let s of semanas) {
            if (dia >= s.inicio && dia <= s.fim) {
                s.total += parseFloat(p.valorTotal || 0);
                s.qtd += p.quantidade !== undefined ? p.quantidade : 1;
                break;
            }
        }
    });

    tbody.innerHTML = semanas.map(s => {
        const mesStr = mes < 10 ? '0' + mes : mes;
        const pd = `${s.inicio < 10 ? '0' + s.inicio : s.inicio}/${mesStr} a ${s.fim}/${mesStr}`;
        const corTotal = (banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
        return `
            <tr>
                <td style="text-align:center;font-weight:600;">${s.nome}</td>
                <td style="text-align:center;font-size:12px;">${pd}</td>
                <td style="text-align:center;font-weight:700;">${s.qtd}</td>
                <td style="text-align:center;font-weight:700;color:${corTotal};">${formatarMoeda(s.total)}</td>
            </tr>
        `;
    }).join('');
}

function renderizarGraficoBarrasMensalOpAdm(resultadoMesAMes, banco) {
    const el = document.getElementById('grafico-barras-faturamento-mensal-adm-op');
    if (!el || !resultadoMesAMes || resultadoMesAMes.length === 0) return;

    // mes_nome vem do backend (Jan, Fev, ...) — campo correto após refatoração
    const meses = resultadoMesAMes.map(m => m.mes_nome || (typeof m.mes === 'string' ? m.mes.substring(0, 3) : String(m.mes)));
    const faturamentos = resultadoMesAMes.map(m => m.faturamento || 0);
    const maxVal = Math.max(...faturamentos, 100);

    const options = {
        series: [
            { name: 'Faturamento', data: faturamentos }
        ],
        chart: {
            type: 'bar',
            height: 220,
            toolbar: { show: false },
            fontFamily: 'Inter, sans-serif'
        },
        colors: [banco === 'AGORACRED' ? '#10B981' : '#7e3d97'],
        plotOptions: {
            bar: {
                borderRadius: 4,
                columnWidth: '65%',
                dataLabels: { position: 'top' }
            }
        },
        dataLabels: {
            enabled: true,
            enabledOnSeries: [0],
            formatter: function (val) {
                if (!val || val === 0) return '';
                return val >= 1000 ? 'R$ ' + (val / 1000).toFixed(1) + 'k' : 'R$ ' + val.toFixed(0);
            },
            style: { fontSize: '11px', fontWeight: '700', colors: [banco === 'AGORACRED' ? '#047857' : '#6b21a8'] },
            offsetY: -22
        },
        grid: { padding: { top: 25 } },
        xaxis: {
            categories: meses,
            labels: { style: { fontSize: '11px', colors: '#374151', fontWeight: 600 } }
        },
        yaxis: {
            max: maxVal * 1.25,
            labels: {
                formatter: function (val) {
                    return val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val;
                },
                style: { fontSize: '12px', colors: '#374151', fontWeight: 600 }
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return formatarMoeda(val);
                }
            }
        },
        legend: { show: true, position: 'top', fontSize: '11px' },
        grid: { padding: { top: 25 } }
    };

    if (chartMensalOpAdm) {
        chartMensalOpAdm.destroy();
    }

    chartMensalOpAdm = new ApexCharts(el, options);
    chartMensalOpAdm.render();
}

function renderizarVariacaoDetalhadaAdmOp(lista) {
    const tbody = document.getElementById('tabela-variacao-detalhada-adm-op');
    if (!tbody) return;

    if (!lista || lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#6B7280;padding:20px;">Nenhum histórico disponível</td></tr>';
        return;
    }

    // Filtra só meses com meta definida
    const comMeta = lista.filter(item => (item.meta || 0) > 0);
    if (comMeta.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#6B7280;padding:20px;">Nenhum mês com meta definida no período</td></tr>';
        return;
    }

    let prevFat = null;
    let prevPerc = null;

    tbody.innerHTML = comMeta.map((item, idx) => {
        const varR = prevFat !== null ? (item.faturamento - prevFat) : 0;
        const varPct = prevFat !== null && prevFat > 0 ? ((item.faturamento - prevFat) / prevFat) * 100 : 0;
        const varMeta = prevPerc !== null ? (item.perc_meta - prevPerc) : 0;

        const corVar = varR >= 0 ? '#16a34a' : '#dc2626';
        const setaVar = varR >= 0 ? '<i class="fas fa-arrow-up"></i>' : '<i class="fas fa-arrow-down"></i>';

        // suporte aos campos do backend (mes_nome, contratos) e legado
        const nomeMes = item.mes_nome || item.periodo || (typeof item.mes === 'string' ? item.mes : String(item.mes));
        const contratos = item.contratos ?? item.quantidade ?? 0;
        const perc = typeof item.perc_meta === 'number' ? item.perc_meta : 0;

        const html = `
            <tr style="background:${idx % 2 === 0 ? '#fff' : '#f9fafb'}">
                <td style="text-align:center;font-weight:600;">${nomeMes}</td>
                <td style="text-align:center;font-weight:700;">${formatarMoeda(item.faturamento)}</td>
                <td style="text-align:center;">${contratos}</td>
                <td style="text-align:center;">${formatarMoeda(item.meta)}</td>
                <td style="text-align:center;">
                    <div style="display:flex;align-items:center;gap:6px;justify-content:center;">
                        <div style="width:60px;height:6px;background:#e5e7eb;border-radius:3px;overflow:hidden;">
                            <div style="width:${Math.min(perc, 100)}%;height:100%;background:var(--purple-main);"></div>
                        </div>
                        <span style="font-weight:700;color:var(--purple-main);">${perc.toFixed(1)}%</span>
                    </div>
                </td>
                <td style="text-align:center;font-weight:700;color:${corVar};">${prevFat !== null ? (varR >= 0 ? '+' : '') + formatarMoeda(varR) : '—'}</td>
                <td style="text-align:center;font-weight:700;color:${corVar};">${prevFat !== null ? setaVar + ' ' + Math.abs(varPct).toFixed(1) + '%' : '—'}</td>
                <td style="text-align:center;font-weight:700;color:${varMeta >= 0 ? '#16a34a' : '#dc2626'};">${prevPerc !== null ? (varMeta >= 0 ? '+' : '') + varMeta.toFixed(1) + 'pp' : '—'}</td>
            </tr>
        `;

        prevFat = item.faturamento;
        prevPerc = item.perc_meta;
        return html;
    }).join('');
}

// Funções de controle de banco e filtros do Dashboard
function filtrarBancoDashboardAdm() {
    const banco = document.getElementById('filtro-banco-adm')?.value || 'TODOS';
    
    // Esconde ou exibe os cards de faturamento correspondentes
    const colSemear = document.getElementById('col-card-semear');
    const colAgoracred = document.getElementById('col-card-agoracred');
    if (colSemear && colAgoracred) {
        if (banco === 'SEMEAR') {
            colSemear.style.display = 'block';
            colSemear.className = 'col-12';
            colAgoracred.style.display = 'none';
        } else if (banco === 'AGORACRED') {
            colSemear.style.display = 'none';
            colAgoracred.style.display = 'block';
            colAgoracred.className = 'col-12';
        } else {
            colSemear.style.display = 'block';
            colSemear.className = 'col-6';
            colAgoracred.style.display = 'block';
            colAgoracred.className = 'col-6';
        }
    }

    // Repopula o dropdown/datalist de operadores baseando-se no banco
    if (dadosAdmCompletos) {
        preencherOperadores(dadosAdmCompletos);
    }
    
    // Reseta a busca de operador ativo ao trocar de banco
    const buscaInput = document.getElementById('busca-operador-adm');
    if (buscaInput) buscaInput.value = '';
    
    const selGlobal = document.getElementById('filtro-operador-adm');
    if (selGlobal) {
        selGlobal.value = 'TODOS';
        carregarDadosAdm();
    }
}

function limparFiltroOperadorDashboardAdm() {
    const buscaInput = document.getElementById('busca-operador-adm');
    if (buscaInput) buscaInput.value = '';
    const selGlobal = document.getElementById('filtro-operador-adm');
    if (selGlobal) {
        selGlobal.value = 'TODOS';
        const event = new Event('change');
        selGlobal.dispatchEvent(event);
    }
}

// Expõe globalmente as novas funções
window.selecionarOperadorPerfAdm = selecionarOperadorPerfAdm;
window.filtrarBancoDashboardAdm = filtrarBancoDashboardAdm;
window.limparFiltroOperadorDashboardAdm = limparFiltroOperadorDashboardAdm;

/**
 * Formata datas de acionamento do formato americano (YYYY-MM-DD HH:MM:SS) para o formato brasileiro (DD/MM/YYYY HH:MM).
 * Se o valor for vazio, nulo ou inválido, retorna '—'.
 */
function _fmtAcion(valor) {
    if (!valor || valor === '-' || valor === 'nan') return '—';
    try {
        // Se a data já estiver no formato brasileiro, retorna direto
        if (valor.includes('/') && !valor.includes('-')) return valor;
        
        // Tenta fazer o split da data e hora
        const partesEspaco = valor.split(' ');
        const dataParte = partesEspaco[0];
        const horaParte = partesEspaco[1] || '';
        
        const partesData = dataParte.split('-');
        if (partesData.length !== 3) return valor;
        
        const dataFmt = `${partesData[2]}/${partesData[1]}/${partesData[0]}`;
        if (horaParte) {
            const partesHora = horaParte.split(':');
            const horaFmt = `${partesHora[0]}:${partesHora[1]}`;
            return `${dataFmt} ${horaFmt}`;
        }
        return dataFmt;
    } catch (e) {
        return valor;
    }
}
window._fmtAcion = _fmtAcion;

// ================================================================
// EXPORT - CSV DO RECEBIMENTO DIÁRIO (Visão Operador Individual — ADM)
// ================================================================

/**
 * Exporta para CSV a tabela de Recebimento Diário do operador individual
 * visualizado pelo ADM. Lê os dados de window._admOpSelecionadoData.performance_diaria.
 */
function exportarPerformanceDiariaAdmOpCSV() {
    const dadosOp = window._admOpSelecionadoData || {};
    const diarios = dadosOp.performance_diaria || [];

    if (!diarios || diarios.length === 0) {
        alert('Nenhum dado de recebimento diário para exportar.');
        return;
    }

    const perf  = dadosOp.performance || {};
    const login = perf.login || 'operador';

    const cabecalhos = ['Data', 'Dia Útil', 'Qtd. Pgtos', 'Recebimento (R$)', 'Meta Diária', 'Bateu Meta?'];

    const linhas = diarios.map(d => {
        // O backend fornece realizado_num (numérico) além de realizado (string formatada)
        const realizadoNum = d.realizado_num != null
            ? d.realizado_num
            : parseFloat((d.realizado || '0').replace(/[^\d,.-]/g, '').replace(',', '.')) || 0;

        const metaDiariaRaw = d.meta_diaria || '0';
        const metaDiariaNum = typeof metaDiariaRaw === 'number'
            ? metaDiariaRaw
            : parseFloat(metaDiariaRaw.replace(/[^\d,.-]/g, '').replace(',', '.')) || 0;

        return [
            d.data_formatada || d.data || '—',
            d.dia_util || '—',
            d.quantidade ?? d.qtd ?? 0,
            realizadoNum.toFixed(2).replace('.', ','),
            metaDiariaNum.toFixed(2).replace('.', ','),
            (d.meta_batida || 'Não').replace(/[^\w\sÀ-ú]/g, '').trim()
        ].join(';');
    });

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    _dispararDownloadCSVAdm(csv, `recebimento_diario_${login}_${new Date().toISOString().split('T')[0]}.csv`);
}

// ================================================================
// EXPORT - CSV DO RESULTADO MÊS A MÊS (Visão Operador Individual — ADM)
// ================================================================

/**
 * Exporta para CSV o Resultado Mês a Mês do operador individual.
 * Lê os dados de window._admOpSelecionadoData.resultado_mes_a_mes.
 */
function exportarResultadoMesAdmOpCSV() {
    const dadosOp = window._admOpSelecionadoData || {};
    const lista   = dadosOp.resultado_mes_a_mes || [];

    if (!lista || lista.length === 0) {
        alert('Nenhum dado de Resultado Mês a Mês para exportar.');
        return;
    }

    const perf  = dadosOp.performance || {};
    const login = perf.login || 'operador';

    const cabecalhos = ['Mês', 'Quantidade', 'Faturamento (R$)', 'Meta (R$)', '% Meta', 'Bateu?', 'Projeção (R$)', '% Projeção'];

    const linhas = lista.map(item => [
        item.mes || item.label || '—',
        item.quantidade || 0,
        (item.faturamento || 0).toFixed(2).replace('.', ','),
        (item.meta        || 0).toFixed(2).replace('.', ','),
        (item.perc_meta   || (item.meta > 0 ? (item.faturamento / item.meta) * 100 : 0)).toFixed(1).replace('.', ',') + '%',
        item.bateu || '—',
        (item.projecao || 0).toFixed(2).replace('.', ','),
        (item.projecao_percentual || 0).toFixed(1).replace('.', ',') + '%'
    ].join(';'));

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    _dispararDownloadCSVAdm(csv, `resultado_mes_a_mes_${login}_${new Date().toISOString().split('T')[0]}.csv`);
}

// ================================================================
// EXPORT - HELPER: dispara download de blob CSV (App ADM)
// ================================================================

function _dispararDownloadCSVAdm(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href     = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ================================================================
// FILTRO DE INTERVALO — ABA DE OPERADORES ADM
// ================================================================

/**
 * Aplica o filtro de intervalo de período na aba de Operadores do ADM.
 * Calcula data_inicio e data_fim com base no intervalo selecionado
 * e aciona o carregamento de dados completo.
 *
 * Intervalos disponíveis:
 *   mes_atual  → mês corrente (sem filtro de range, usa ano/mês)
 *   3_meses    → últimos 3 meses completos até hoje
 *   6_meses    → últimos 6 meses completos até hoje
 *   12_meses   → últimos 12 meses completos até hoje
 */
function aplicarIntervaloOperadores() {
    const sel = document.getElementById('filtro-intervalo-operadores-adm');
    if (!sel) return;

    const intervalo = sel.value;
    const hoje = new Date();

    // Obtém os campos de data global do dashboard
    const dataInicioEl = document.getElementById('filtro-data-inicio-adm');
    const dataFimEl    = document.getElementById('filtro-data-fim-adm');
    const mesEl        = document.getElementById('filtro-mes-adm');
    const anoEl        = document.getElementById('filtro-ano-adm');

    if (intervalo === 'mes_atual') {
        // Limpa os filtros de range e volta ao mês/ano atual
        if (dataInicioEl) dataInicioEl.value = '';
        if (dataFimEl)    dataFimEl.value    = '';
        // Garante que mês e ano estejam no valor atual
        if (mesEl) mesEl.value = String(hoje.getMonth() + 1).padStart(2, '0');
        if (anoEl) anoEl.value = String(hoje.getFullYear());
    } else {
        // Calcula quantos meses recuar
        const mesesRecuar = intervalo === '3_meses' ? 3 : intervalo === '6_meses' ? 6 : 12;

        // Data fim = hoje
        const dataFim = new Date(hoje);
        const yyyy_fim = dataFim.getFullYear();
        const mm_fim   = String(dataFim.getMonth() + 1).padStart(2, '0');
        const dd_fim   = String(dataFim.getDate()).padStart(2, '0');
        const strFim   = `${yyyy_fim}-${mm_fim}-${dd_fim}`;

        // Data início = 1º dia do mês de N meses atrás
        const dataInicio = new Date(hoje.getFullYear(), hoje.getMonth() - mesesRecuar + 1, 1);
        const yyyy_ini   = dataInicio.getFullYear();
        const mm_ini     = String(dataInicio.getMonth() + 1).padStart(2, '0');
        const strInicio  = `${yyyy_ini}-${mm_ini}-01`;

        if (dataInicioEl) dataInicioEl.value = strInicio;
        if (dataFimEl)    dataFimEl.value    = strFim;

        // Atualiza mês/ano para o mês atual (necessário para a API)
        if (mesEl) mesEl.value = String(hoje.getMonth() + 1).padStart(2, '0');
        if (anoEl) anoEl.value = String(hoje.getFullYear());
    }

    // Recarrega os dados com os novos filtros
    if (typeof carregarDadosAdm === 'function') {
        carregarDadosAdm();
    }
}

// Expõe funções ao escopo global
window.exportarPerformanceDiariaAdmOpCSV = exportarPerformanceDiariaAdmOpCSV;
window.exportarResultadoMesAdmOpCSV      = exportarResultadoMesAdmOpCSV;
window.aplicarIntervaloOperadores        = aplicarIntervaloOperadores;

// ================================================================
// VISÃO PERIÓDICA — ADM (operador individual)
// ================================================================

// Dados da visão periódica do operador atualmente visualizado
let _visaoPeriodicaAdmDados = [];

/**
 * Seleciona visualmente o botão de período e dispara o carregamento.
 */
function selecionarPeriodoAdm(btn, meses) {
    document.querySelectorAll('.btn-periodo-adm').forEach(b => {
        b.style.background = 'transparent';
        b.style.color      = 'var(--purple-main)';
    });
    btn.style.background = 'var(--purple-main)';
    btn.style.color      = 'white';

    const login = window._admOpAtual || null;
    const banco = window._admBancoAtual || 'SEMEAR';
    if (!login) return;
    carregarVisaoPeriodicaAdm(login, banco, meses);
}
window.selecionarPeriodoAdm = selecionarPeriodoAdm;

/**
 * Busca dados da API para o intervalo de N meses e renderiza a visão periódica.
 * @param {string} login  - login do operador
 * @param {string} banco  - 'SEMEAR' | 'AGORACRED'
 * @param {number} meses  - quantidade de meses (1, 3, 6, 12)
 */
async function carregarVisaoPeriodicaAdm(login, banco, meses) {
    const secao   = document.getElementById('secao-visao-periodica-adm');
    const loading = document.getElementById('span-loading-periodica-adm');
    const label   = document.getElementById('label-periodo-adm');
    const tbody   = document.getElementById('tabela-periodica-adm');

    if (!secao) return;
    secao.style.display = 'block';
    if (loading) loading.style.display = 'inline';
    if (tbody)   tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:20px;"><i class="fas fa-spinner fa-spin"></i> Carregando...</td></tr>';

    const hoje    = new Date();
    const dataFim = `${hoje.getFullYear()}-${String(hoje.getMonth()+1).padStart(2,'0')}-${String(hoje.getDate()).padStart(2,'0')}`;
    const ini     = new Date(hoje.getFullYear(), hoje.getMonth() - meses + 1, 1);
    const dataIni = `${ini.getFullYear()}-${String(ini.getMonth()+1).padStart(2,'0')}-01`;

    const mesesNomes = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
    if (label) label.textContent = `${mesesNomes[ini.getMonth()]}/${ini.getFullYear()} — ${mesesNomes[hoje.getMonth()]}/${hoje.getFullYear()}`;

    // Calcula meses dentro do período
    const mesesNoPeriodo = [];
    const cursor = new Date(ini.getFullYear(), ini.getMonth(), 1);
    while (cursor <= hoje) {
        mesesNoPeriodo.push(cursor.getMonth() + 1);
        cursor.setMonth(cursor.getMonth() + 1);
    }

    // ── Para CONSOLIDADO usa os dados já carregados (sem chamar /api/resumo) ──
    const isConsolidado = login === 'CONSOLIDADO_SEMEAR' || login === 'CONSOLIDADO_AGORACRED';
    if (isConsolidado) {
        const bancoDados = banco === 'AGORACRED' ? dadosAdmCompletos.agoracred : dadosAdmCompletos.semear;
        const listaConsolidada = ((bancoDados && bancoDados.resultado_mes_a_mes) || [])
            .filter(item => mesesNoPeriodo.includes(item.mes_num));
        _visaoPeriodicaAdmDados = listaConsolidada;
        renderizarKPIsPeriodicaAdm(listaConsolidada);
        renderizarTabelaPeriodicaAdm(listaConsolidada);
        renderizarFaixasPeriodica(null, banco); // sem faixas individuais no consolidado
        if (loading) loading.style.display = 'none';
        return;
    }

    try {
        const resp = await fetch(`/api/resumo/${login}?data_inicio=${dataIni}&data_fim=${dataFim}`);
        const json = await resp.json();
        if (!json.success) throw new Error(json.message || 'Erro na API');

        const lista = (json.data.resultado_mes_a_mes || []).filter(item =>
            mesesNoPeriodo.includes(item.mes_num)
        );
        _visaoPeriodicaAdmDados = lista;
        renderizarKPIsPeriodicaAdm(lista);
        renderizarTabelaPeriodicaAdm(lista);

        // Faixas de atraso do período (apenas SEMEAR)
        const faixasPeriodo = banco === 'SEMEAR' ? (json.data.faixas_operador || null) : null;
        renderizarFaixasPeriodica(faixasPeriodo, banco);
    } catch (e) {
        console.error('[Visão Periódica ADM]', e);
        if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#dc2626;padding:20px;">Erro ao carregar: ${e.message}</td></tr>`;
    } finally {
        if (loading) loading.style.display = 'none';
    }
}
window.carregarVisaoPeriodicaAdm = carregarVisaoPeriodicaAdm;

/** Preenche os KPI cards com totais acumulados do período. */
function renderizarKPIsPeriodicaAdm(lista) {
    const totalFat  = lista.reduce((s, i) => s + (i.faturamento || 0), 0);
    const totalMeta = lista.reduce((s, i) => s + (i.meta       || 0), 0);
    const totalQtd  = lista.reduce((s, i) => s + (i.quantidade || 0), 0);
    const pctMeta   = totalMeta > 0 ? (totalFat / totalMeta * 100).toFixed(1) : '0.0';

    const el = id => document.getElementById(id);
    if (el('kpi-periodica-fat-adm'))  el('kpi-periodica-fat-adm').textContent  = formatarMoeda(totalFat);
    if (el('kpi-periodica-meta-adm')) el('kpi-periodica-meta-adm').textContent = formatarMoeda(totalMeta);
    if (el('kpi-periodica-perc-adm')) el('kpi-periodica-perc-adm').textContent = `${pctMeta}%`;
    if (el('kpi-periodica-qtd-adm'))  el('kpi-periodica-qtd-adm').textContent  = totalQtd;
}

/** Renderiza a tabela mês a mês da visão periódica. */
function renderizarTabelaPeriodicaAdm(lista) {
    const tbody = document.getElementById('tabela-periodica-adm');
    if (!tbody) return;
    if (!lista || lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:20px;">Nenhum dado no período</td></tr>';
        return;
    }
    tbody.innerHTML = lista.map((item, idx) => {
        const bateuCor = item.bateu === 'Sim' ? '#16a34a' : '#dc2626';
        const bateuBg  = item.bateu === 'Sim' ? '#dcfce7' : '#fee2e2';
        const bg = idx % 2 === 0 ? '#fff' : '#faf5ff';
        const percFmt = (item.perc_meta || 0).toFixed(1) + '%';
        return `<tr style="background:${bg};">
            <td style="padding:9px 14px;text-align:center;font-weight:600;">${item.mes || '-'}</td>
            <td style="padding:9px 14px;text-align:center;">${item.quantidade || 0}</td>
            <td style="padding:9px 14px;text-align:center;font-weight:600;">${formatarMoeda(item.faturamento || 0)}</td>
            <td style="padding:9px 14px;text-align:center;">${formatarMoeda(item.meta || 0)}</td>
            <td style="padding:9px 14px;text-align:center;font-weight:700;">${percFmt}</td>
            <td style="padding:9px 14px;text-align:center;"><span style="background:${bateuBg};color:${bateuCor};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;">${item.bateu || '-'}</span></td>
        </tr>`;
    }).join('');
}

/**
 * Exporta CSV da Visão Periódica (admin).
 */
function exportarVisaoPeriodicaAdmCSV() {
    const lista = _visaoPeriodicaAdmDados || [];
    if (!lista || lista.length === 0) {
        alert('Nenhum dado periódico para exportar.');
        return;
    }
    const cabecalhos = ['Mês', 'Qtd. Pgtos', 'Faturamento (R$)', 'Meta (R$)', '% Meta', 'Bateu Meta?'];
    const linhas = lista.map(item => [
        item.mes || '-',
        item.quantidade || 0,
        (item.faturamento || 0).toFixed(2).replace('.',','),
        (item.meta        || 0).toFixed(2).replace('.',','),
        (item.perc_meta   || 0).toFixed(1).replace('.',',') + '%',
        item.bateu || '-'
    ].join(';'));
    // Totais
    const tFat  = lista.reduce((s, i) => s + (i.faturamento || 0), 0);
    const tMeta = lista.reduce((s, i) => s + (i.meta || 0), 0);
    const tQtd  = lista.reduce((s, i) => s + (i.quantidade || 0), 0);
    const tPerc = tMeta > 0 ? (tFat / tMeta * 100).toFixed(1) : '0.0';
    linhas.push(['TOTAL ACÚMULADO', tQtd, tFat.toFixed(2).replace('.',','), tMeta.toFixed(2).replace('.',','), `${tPerc.replace('.',',')}%`, ''].join(';'));

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    const login = window._admOpAtual || 'operador';
    _dispararDownloadCSVAdm(csv, `visao_periodica_${login}_${new Date().toISOString().split('T')[0]}.csv`);
}
window.exportarVisaoPeriodicaAdmCSV = exportarVisaoPeriodicaAdmCSV;

// ================================================================
// PIVOT: alternância SEMEAR ↔ AGORACRED (Mês × Operador)
// ================================================================
function alterarPivotBanco(banco) {
    const btnS  = document.getElementById('btn-pivot-semear');
    const btnA  = document.getElementById('btn-pivot-agoracred');
    const head  = document.getElementById('thead-mes-operador-adm');
    const thOp  = document.getElementById('th-op-sticky');
    const tit   = document.getElementById('titulo-mes-operador-adm');
    if (banco === 'SEMEAR') {
        if (btnS) { btnS.style.background = '#7E3E9A'; btnS.style.color = 'white'; }
        if (btnA) { btnA.style.background = 'transparent'; btnA.style.color = '#10b981'; }
        if (head) head.style.background = '#7E3E9A';
        if (thOp) thOp.style.background = '#7E3E9A';
        if (tit)  tit.style.color = '#7E3E9A';
        renderizarMesOperadorAdm(window._pivotSemear || [], 'SEMEAR');
    } else {
        if (btnS) { btnS.style.background = 'transparent'; btnS.style.color = '#7E3E9A'; }
        if (btnA) { btnA.style.background = '#10b981'; btnA.style.color = 'white'; }
        if (head) head.style.background = '#10b981';
        if (thOp) thOp.style.background = '#10b981';
        if (tit)  tit.style.color = '#10b981';
        renderizarMesOperadorAdm(window._pivotAgoracred || [], 'AGORACRED');
    }
}
window.alterarPivotBanco = alterarPivotBanco;