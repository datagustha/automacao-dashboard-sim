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

    // Coleta todas as datas de pagamento de todos os operadores (semear + agoracred)
    const todasDatas = [];
    const bancos = ['semear', 'agoracred'];
    bancos.forEach(b => {
        const ops = dados[b]?.operadores || [];
        ops.forEach(op => {
            const ult = op.ultimo_pagamento || op.ultima_data;
            if (ult) todasDatas.push(ult);
        });
        // Também tenta a evolução
        const evol = dados[b]?.evolucao || [];
        evol.forEach(e => { if (e.data) todasDatas.push(e.data); });
    });

    if (todasDatas.length === 0) {
        el.textContent = '';
        return;
    }

    // Pega a mais recente
    todasDatas.sort();
    const ultData = todasDatas[todasDatas.length - 1];
    if (!ultData || !ultData.includes('-')) { el.textContent = ''; return; }

    const partes = ultData.split('-');
    const dataFmt = `${partes[2]}/${partes[1]}/${partes[0]}`;
    el.innerHTML = `<i class="fas fa-clock" style="margin-right:4px;color:#a855f7;"></i>Últ. receb.: <strong>${dataFmt}</strong>`;
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

    // Se estiver na aba Operadores, oculta o multiselect de operadores do topo global
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
        dias_restantes: diasRestantes
    };

    // Meta diária consolidada do banco
    const metaDiaria = totalDiasUteis > 0 ? (meta / totalDiasUteis) : 0;

    // Mapeia a evolução diária (faturamento diário consolidado)
    const performanceDiaria = (dadosBanco.evolucao || []).map(ev => {
        const dia = ev.data ? parseInt(ev.data.split('-')[2], 10) : 0;
        const realizadoVal = ev.total || 0;
        const bateu = realizadoVal >= metaDiaria ? 'Sim' : 'Não';
        return {
            dia: dia,
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
    const sel = document.getElementById('filtro-operador-perf-adm');
    if (!sel) return;

    // Salva o valor atualmente selecionado
    const valAtual = sel.value;

    // Limpa e repovoa com apenas as visões consolidadas (sem individuais)
    sel.innerHTML = '';

    if (banco === 'TODOS' || banco === 'SEMEAR') {
        const optSem = document.createElement('option');
        optSem.value = 'CONSOLIDADO_SEMEAR';
        optSem.textContent = 'Visão Geral Consolidada — SEMEAR';
        sel.appendChild(optSem);
    }
    if (banco === 'TODOS' || banco === 'AGORACRED') {
        const optAgo = document.createElement('option');
        optAgo.value = 'CONSOLIDADO_AGORACRED';
        optAgo.textContent = 'Visão Geral Consolidada — AGORACRED';
        sel.appendChild(optAgo);
    }

    const optTabela = document.createElement('option');
    optTabela.value = 'LISTA_OPERADORES';
    optTabela.textContent = 'Lista Geral de Operadores (Tabela)';
    sel.appendChild(optTabela);

    // Recupera valor se ainda existir na lista de opções
    if (Array.from(sel.options).some(opt => opt.value === valAtual)) {
        sel.value = valAtual;
    } else {
        sel.value = banco === 'AGORACRED' ? 'CONSOLIDADO_AGORACRED' : 'CONSOLIDADO_SEMEAR';
    }

    console.log(`[ADM FILTROS] Filtros de operadores atualizados. Banco: ${banco}`);
}

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
        
        const dadosConsolidados = obterDadosConsolidadosBanco(banco);
        if (dadosConsolidados) {
            renderizarMinhaPerformanceOpAdm(dadosConsolidados, mes, ano);
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
            
            renderizarMinhaPerformanceOpAdm(_admOpSelecionadoData, mes, ano);

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
    document.getElementById('adm-op-dias-rest').textContent = perf.dias_restantes || 0;
    document.getElementById('adm-op-total-dias').textContent = perf.total_dias_uteis || 0;

    // --- 3. RECEBIMENTO DIÁRIO ---
    const tbodyDiario = document.getElementById('tabela-recebimento-diario-adm-op');
    if (tbodyDiario) {
        const theadDiario = tbodyDiario.previousElementSibling;
        if (theadDiario) {
            theadDiario.style.backgroundColor = (banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
        }
        if (diarios.length === 0) {
            tbodyDiario.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#6B7280;padding:20px;">Nenhum faturamento registrado nos dias úteis.</td></tr>';
        } else {
            tbodyDiario.innerHTML = diarios.map((d, idx) => {
                // Normaliza campo dia: pode vir como número direto ou extraído do campo 'data'
                let diaNum = d.dia;
                let dataStr = d.data || d.dtPgto || '';

                if ((diaNum === undefined || diaNum === null || diaNum === 0) && dataStr) {
                    diaNum = parseInt(dataStr.split('-')[2], 10) || 0;
                }

                // Data formatada: usa dataStr se disponível, senão reconstrói
                let dataFormatada = '—';
                if (dataStr && dataStr.includes('-')) {
                    const partes = dataStr.split('-');
                    dataFormatada = `${partes[2]}/${partes[1]}/${partes[0]}`;
                } else if (diaNum > 0) {
                    const diaP = diaNum < 10 ? '0' + diaNum : diaNum;
                    const mesP = mes < 10 ? '0' + mes : mes;
                    dataFormatada = `${diaP}/${mesP}/${ano}`;
                }

                const diaExib = diaNum > 0 ? diaNum : '—';
                const qtd = d.quantidade ?? d.qtd ?? d.contratos ?? '—';
                const metaBatida = d.meta_batida || 'Não';

                return `
                    <tr>
                        <td style="text-align:center;font-weight:600;">${diaExib}</td>
                        <td style="text-align:center;">${idx + 1}</td>
                        <td style="text-align:center;">${dataFormatada}</td>
                        <td style="text-align:center;">${qtd}</td>
                        <td style="text-align:center;font-weight:600;">${d.realizado}</td>
                        <td style="text-align:center;">${d.meta_diaria}</td>
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
        const theadMesAPerf = tbodyMesAPerf.previousElementSibling;
        if (theadMesAPerf) {
            theadMesAPerf.style.backgroundColor = (banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
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
    const metas = resultadoMesAMes.map(m => m.meta || 0);

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
            style: { fontSize: '11px', colors: ['#374151'] },
            offsetY: -20
        },
        xaxis: {
            categories: meses,
            labels: { style: { fontSize: '11px', colors: '#374151', fontWeight: 600 } }
        },
        yaxis: {
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