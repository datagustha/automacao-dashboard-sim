/**
 * DASHBOARD - Funções Específicas
 * ================================
 */

// ================================================================
// RENDERIZAÇÃO - DASHBOARD
// ================================================================

let pagamentosRecentesOpData = [];
let pagamentosRecentesOpFiltrados = [];
let pagRecentesOpPage = 1;
const pagRecentesOpPerPage = 10;

function filtrarPagamentosRecentesOp() {
    const busca = (document.getElementById('filtro-recentes-busca')?.value || '').toLowerCase();
    const inicio = document.getElementById('filtro-recentes-inicio')?.value || '';
    const fim = document.getElementById('filtro-recentes-fim')?.value || '';

    let filtrados = pagamentosRecentesOpData;

    if (busca) {
        filtrados = filtrados.filter(p =>
            (p.cliente || '').toLowerCase().includes(busca) ||
            (p.contrato || '').toLowerCase().includes(busca)
        );
    }
    if (inicio) filtrados = filtrados.filter(p => p.dtPgto >= inicio);
    if (fim) filtrados = filtrados.filter(p => p.dtPgto <= fim);

    pagamentosRecentesOpFiltrados = filtrados;
    pagRecentesOpPage = 1;
    renderizarPagamentosRecentesPaginados();
}
window.filtrarPagamentosRecentesOp = filtrarPagamentosRecentesOp;

function renderizarDashboard(dados) {
    if (!dados) {
        console.warn('⚠️ Dados não fornecidos para renderizarDashboard');
        return;
    }
    
    // ============================================================
    // KPIs
    // ============================================================
    const indicadores = dados.indicadores || {};
    const indicadoresAnt = dados.indicadores_anterior || {};
    const performance = dados.performance || {};
    
    // Faturamento
    const faturamento = indicadores.faturamento_total || 0;
    const faturamentoAnt = indicadoresAnt.faturamento_total || 0;
    document.getElementById('kpi-faturamento').textContent = formatarMoeda(faturamento);
    
    // Ticket Médio
    const ticket = indicadores.ticket_medio || 0;
    const ticketAnt = indicadoresAnt.ticket_medio || 0;
    document.getElementById('kpi-ticket').textContent = formatarMoeda(ticket);
    
    // Total de Pagamentos
    const totalPgtos = indicadores.total_pagamentos || 0;
    const totalPgtosAnt = indicadoresAnt.total_pagamentos || 0;
    document.getElementById('kpi-total-pgtos').textContent = totalPgtos;

    // NOTA: o badge do menu lateral "Pagamentos" NÃO é atualizado aqui.
    // Ele sempre mostra a quantidade do mês ATUAL real (não do filtro
    // selecionado) — ver atualizarBadgePagamentosMesAtual() em app.js.

    // Meta
    const meta = performance.meta || 0;
    const atingido = performance.atingido_meta || 0;
    document.getElementById('kpi-meta-objetivo').textContent = formatarMoeda(meta);
    document.getElementById('kpi-meta-barra').style.width = Math.min(atingido, 100) + '%';
    document.getElementById('kpi-meta-percentual').textContent = atingido.toFixed(1) + '%';
    
    // Rodapé de Meta — Faturamento
    const variacaoFat = faturamentoAnt > 0 ? ((faturamento - faturamentoAnt) / faturamentoAnt) * 100 : 0;
    const faltaFat = Math.max(0, meta - faturamento);
    const faltaFatPct = meta > 0 ? (faltaFat / meta) * 100 : 0;
    
    const corVar = variacaoFat >= 0 ? '#16a34a' : '#dc2626';
    const bgVar = variacaoFat >= 0 ? '#dcfce7' : '#fee2e2';
    const seta = variacaoFat >= 0 ? '▲' : '▼';
    const faltaHtml = faltaFat > 0
        ? `<span style="font-weight:700;color:var(--text-main);font-size:11px;">Falta: ${formatarMoeda(faltaFat)}</span>
           <span style="color:#d97706;background:#fef3c7;padding:2px 6px;border-radius:4px;font-weight:700;font-size:10px;margin-left:4px;">${faltaFatPct.toFixed(1)}% abaixo</span>`
        : `<span style="font-weight:700;color:#16a34a;font-size:11px;">Meta Atingida! <i class=\"fas fa-check-circle\"></i></span>`;
        
    const footerMetaEl = document.getElementById('kpi-meta-anterior-detalhe');
    if (footerMetaEl) {
        footerMetaEl.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
                <div>
                    <span style="font-size:10px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                    <div style="display:flex;align-items:center;">
                        <span style="font-weight:700;color:var(--text-main);font-size:11px;">${formatarMoeda(faturamentoAnt)}</span>
                        <span style="color:${corVar};background:${bgVar};padding:2px 6px;border-radius:4px;font-weight:700;font-size:10px;margin-left:6px;">${seta} ${Math.abs(variacaoFat).toFixed(1)}%</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:10px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença da Meta</span>
                    <div style="display:flex;align-items:center;justify-content:flex-end;">${faltaHtml}</div>
                </div>
            </div>
        `;
    }

    // Rodapé - Quantidade de Pagamentos
    const variacaoPgtos = totalPgtosAnt > 0 ? ((totalPgtos - totalPgtosAnt) / totalPgtosAnt) * 100 : 0;
    const difPgtos = totalPgtos - totalPgtosAnt;
    const corVarPgtos = variacaoPgtos >= 0 ? '#16a34a' : '#dc2626';
    const bgVarPgtos = variacaoPgtos >= 0 ? '#dcfce7' : '#fee2e2';
    const setaPgtos = variacaoPgtos >= 0 ? '▲' : '▼';
    const sinalPgtos = difPgtos >= 0 ? '+' : '';

    const footerPgtosEl = document.getElementById('kpi-total-pgtos-anterior-detalhe');
    if (footerPgtosEl) {
        footerPgtosEl.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
                <div>
                    <span style="font-size:10px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                    <div style="display:flex;align-items:center;">
                        <span style="font-weight:700;color:var(--text-main);font-size:11px;">${totalPgtosAnt} pgtos</span>
                        <span style="color:${corVarPgtos};background:${bgVarPgtos};padding:2px 6px;border-radius:4px;font-weight:700;font-size:10px;margin-left:6px;">${setaPgtos} ${Math.abs(variacaoPgtos).toFixed(1)}%</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:10px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença no Período</span>
                    <span style="font-weight:700;color:${corVarPgtos};font-size:11px;">${sinalPgtos}${difPgtos} pgtos</span>
                </div>
            </div>
        `;
    }

    // Rodapé - Ticket Médio
    const variacaoTicket = ticketAnt > 0 ? ((ticket - ticketAnt) / ticketAnt) * 100 : 0;
    const difTicket = ticket - ticketAnt;
    const corVarTk = variacaoTicket >= 0 ? '#16a34a' : '#dc2626';
    const bgVarTk = variacaoTicket >= 0 ? '#dcfce7' : '#fee2e2';
    const setaTk = variacaoTicket >= 0 ? '▲' : '▼';
    const sinalTk = difTicket >= 0 ? '+' : '';

    const footerTkEl = document.getElementById('kpi-ticket-anterior-detalhe');
    if (footerTkEl) {
        footerTkEl.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
                <div>
                    <span style="font-size:10px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                    <div style="display:flex;align-items:center;">
                        <span style="font-weight:700;color:var(--text-main);font-size:11px;">${formatarMoeda(ticketAnt)}</span>
                        <span style="color:${corVarTk};background:${bgVarTk};padding:2px 6px;border-radius:4px;font-weight:700;font-size:10px;margin-left:6px;">${setaTk} ${Math.abs(variacaoTicket).toFixed(1)}%</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:10px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença no Período</span>
                    <span style="font-weight:700;color:${corVarTk};font-size:11px;">${sinalTk}${formatarMoeda(difTicket)}</span>
                </div>
            </div>
        `;
    }
    
    // ============================================================
    // TMA (Métricas de Ligação - Visual Enriquecido)
    // ============================================================
    if (dados.tma) {
        document.getElementById('kpi-tma-valor').textContent = dados.tma.tma || '00:00:00';
        document.getElementById('kpi-tma-falado').innerHTML = `Falado no mês: <strong>${dados.tma.tempo_falado || '0h 00min'}</strong>`;
        
        document.getElementById('kpi-tma-acionamentos').textContent = dados.tma.acionamentos || 0;
        document.getElementById('kpi-tma-ultimo').innerHTML = `Últ. Acion.: <strong>${_formatarDataAcionamento(dados.tma.ultimo_acionamento)}</strong>`;
        
        // Formata reacionamento (ex: "2.10x" ou similar)
        let reacStr = dados.tma.reacionamento || '1.00';
        if (reacStr && !reacStr.toString().endsWith('x')) {
            reacStr = parseFloat(reacStr).toFixed(2) + 'x';
        }
        document.getElementById('kpi-tma-reacionamento').textContent = reacStr;
        document.getElementById('kpi-tma-clientes').innerHTML = `Clientes únicos: <strong>${dados.tma.clientes || 0}</strong>`;
    }

    // ============================================================
    // OCULTAR FASE PARA AGORACRED E EXPANDIR LINHA
    // ============================================================
    const banco = (dados.operador && dados.operador.banco) || 'SEMEAR';
    const containerEvolucao = document.getElementById('container-grafico-evolucao');
    const containerFase = document.getElementById('container-grafico-fase');
    
    if (containerEvolucao && containerFase) {
        if (banco === 'AGORACRED') {
            containerFase.style.display = 'none';
            containerEvolucao.className = 'col-12';
        } else {
            containerFase.style.display = 'block';
            containerEvolucao.className = 'col-6';
        }
    }
    
    // ============================================================
    // GRÁFICOS
    // ============================================================
    const graficoEvolucao = document.getElementById('grafico-evolucao');
    if (graficoEvolucao) {
        graficoEvolucao.innerHTML = criarGraficoEvolucao(dados.faturamento_dia || []);
    }
    
    const graficoFase = document.getElementById('grafico-fase');
    if (graficoFase && banco !== 'AGORACRED') {
        graficoFase.innerHTML = criarGraficoFase(dados.pagamentos_fase || []);
    }
    
    // ============================================================
    // TABELA: PERFORMANCE DO OPERADOR (NOVA NO DASHBOARD PRINCIPAL)
    // ============================================================
    renderizarTabelaPerformanceOpNova(performance);
    
    // ============================================================
    // TABELA: RESULTADO MÊS A MÊS (NOVA NO DASHBOARD PRINCIPAL)
    // ============================================================
    renderizarTabelaResultadoMesAMesNova(dados.resultado_mes_a_mes || []);

    // ============================================================
    // TABELA: RELAÇÃO DE PAGAMENTOS RECENTES (PAGINADA)
    // ============================================================
    pagamentosRecentesOpData = dados.ultimos_pagamentos || [];
    pagamentosRecentesOpFiltrados = pagamentosRecentesOpData;
    pagRecentesOpPage = 1;
    // Limpa os filtros da lista ao recarregar com um novo período
    const buscaEl = document.getElementById('filtro-recentes-busca');
    const inicioEl = document.getElementById('filtro-recentes-inicio');
    const fimEl = document.getElementById('filtro-recentes-fim');
    if (buscaEl) buscaEl.value = '';
    if (inicioEl) inicioEl.value = '';
    if (fimEl) fimEl.value = '';
    renderizarPagamentosRecentesPaginados();
    
    // ============================================================
    // EVOLUÇÃO
    // ============================================================
    renderizarEvolucao(dados);

    // ============================================================
    // VISÃO TRIMESTRAL POR DIA ÚTIL (OPERADOR)
    // Compara faturamento dos 3 últimos meses por dia útil.
    // ============================================================
    if (typeof renderizarTrimestreDUOp === 'function') {
        renderizarTrimestreDUOp(dados.trimestre_du || null);
    }

    // ============================================================
    // RELATÓRIO FAIXA DE ATRASO VS MÊS (EXCLUSIVO SEMEAR)
    // Mostra faturamento por faixa de atraso em cada mês do ano.
    // ============================================================
    if (typeof renderizarMatrizFaixasOp === 'function') {
        const bancoOp = (dados.operador && dados.operador.banco) || 'SEMEAR';
        if (bancoOp === 'SEMEAR') {
            renderizarMatrizFaixasOp(dados.matriz_faixas_mes || null);
        } else {
            // Oculta o card para AGORACRED
            const containerFaixas = document.getElementById('card-faixas-vs-mes-op-container');
            if (containerFaixas) containerFaixas.style.display = 'none';
        }
    }

    // ============================================================
    // ALERTA DE INATIVIDADE (> 2 DIAS SEM RECEBIMENTO)
    // Banner exibido no topo da página do operador.
    // ============================================================
    (() => {
        // Usa o id real do HTML: alerta-sem-pgto-modal
        const banner = document.getElementById('alerta-sem-pgto-modal');
        if (!banner) return;
        const perf = dados.performance || {};
        const diasSem = perf.dias_sem_pgto;

        if (diasSem !== undefined && diasSem >= 2) {
            banner.style.display = 'block';
            const titulo = document.getElementById('alerta-sem-pgto-titulo');
            if (titulo) {
                titulo.textContent = `⚠️ ATENÇÃO: Você está há ${diasSem} dias úteis sem registrar recebimentos!`;
            }
        } else {
            banner.style.display = 'none';
        }
    })();
}

// ================================================================
// RENDERIZAÇÃO - PERFORMANCE
// ================================================================

function renderizarPerformance(performance) {
    if (!performance) {
        const tbody = document.getElementById('tabela-performance');
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#6B7280;padding:30px;">Sem dados de performance</td></tr>`;
        }
        return;
    }
    
    const tbody = document.getElementById('tabela-performance');
    if (!tbody) return;
    
    tbody.innerHTML = `
        <tr>
            <td><strong>${formatarMoeda(performance.meta || 0)}</strong></td>
            <td>${formatarMoeda(performance.faturamento || 0)}</td>
            <td>${(performance.atingido_meta || 0).toFixed(1)}%</td>
            <td>${formatarMoeda(performance.projecao || 0)}</td>
            <td>${performance.dias_trabalhados || 0}/${performance.total_dias_uteis || 0}</td>
        </tr>
    `;
}

// ================================================================
// RENDERIZAÇÃO - VISÃO TRIMESTRAL POR DIA ÚTIL (OPERADOR)
// Recebe o objeto trimestre_du com: { colunas, linhas, totais }
// ================================================================

function renderizarTrimestreDUOp(dados) {
    const tbody = document.getElementById('tabela-trimestre-du-op');
    if (!tbody) return;

    if (!dados || !dados.linhas || dados.linhas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#95a5a6;padding:20px;">Sem dados trimestrais disponíveis para o período.</td></tr>';
        return;
    }

    // Atualiza cabeçalhos com nomes dos meses reais
    const colunas = dados.colunas || [];
    const nomesCols = ['th-trimestre-m0', 'th-trimestre-m1', 'th-trimestre-m2'];
    colunas.forEach((col, i) => {
        const el = document.getElementById(nomesCols[i]);
        if (el) el.textContent = col;
    });

    const linhas = dados.linhas || [];
    let html = '';

    linhas.forEach(linha => {
        const vAtual = linha.v_atual || 0;
        const vM1 = linha.v_m1 || 0;
        const vM2 = linha.v_m2 || 0;

        // Destaque verde se mês atual > mês anterior
        const corAtual = vAtual > vM1 ? '#16a34a' : (vAtual < vM1 ? '#dc2626' : '#374151');
        const bgAtual = vAtual > vM1 ? '#dcfce7' : (vAtual < vM1 ? '#fee2e2' : 'transparent');

        html += `
            <tr style="border-bottom:1px solid #f0f0f0;">
                <td style="padding:8px 14px;text-align:center;font-weight:700;color:#7c3aed;">${linha.dia_util || '-'}</td>
                <td style="padding:8px 14px;text-align:center;color:var(--text-muted);">${linha.data_atual || '-'}</td>
                <td style="padding:8px 14px;text-align:center;font-weight:700;color:${corAtual};background:${bgAtual};border-radius:6px;">${formatarMoeda(vAtual)}</td>
                <td style="padding:8px 14px;text-align:center;color:#374151;">${vM1 > 0 ? formatarMoeda(vM1) : '<span style="color:#9ca3af;">—</span>'}</td>
                <td style="padding:8px 14px;text-align:center;color:#374151;">${vM2 > 0 ? formatarMoeda(vM2) : '<span style="color:#9ca3af;">—</span>'}</td>
            </tr>
        `;
    });

    // Linha de totais
    if (dados.totais) {
        const t = dados.totais;
        html += `
            <tr style="background:#ede9fe;font-weight:800;border-top:2px solid #7c3aed;">
                <td colspan="2" style="padding:10px 14px;text-align:center;color:#4a1d8c;">TOTAL DO PERÍODO</td>
                <td style="padding:10px 14px;text-align:center;color:#7c3aed;">${formatarMoeda(t.v_atual || 0)}</td>
                <td style="padding:10px 14px;text-align:center;color:#6d28d9;">${t.v_m1 > 0 ? formatarMoeda(t.v_m1) : '—'}</td>
                <td style="padding:10px 14px;text-align:center;color:#5b21b6;">${t.v_m2 > 0 ? formatarMoeda(t.v_m2) : '—'}</td>
            </tr>
        `;
    }

    tbody.innerHTML = html;
}

// ================================================================
// RENDERIZAÇÃO - RELATÓRIO FAIXA DE ATRASO VS MÊS (OPERADOR)
// Recebe o objeto matriz_faixas_mes com: { ano, meses, linhas, totais }
// Exibido somente para operadores SEMEAR.
// ================================================================

function renderizarMatrizFaixasOp(dados) {
    const container = document.getElementById('card-faixas-vs-mes-op-container');
    const tbody = document.getElementById('tabela-faixa-vs-mes-op');
    if (!tbody) return;

    if (!dados || !dados.linhas || dados.linhas.length === 0) {
        if (container) container.style.display = 'none';
        return;
    }

    // Exibe o container (oculto por padrão, só aparece para SEMEAR)
    if (container) container.style.display = 'block';

    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    const linhas = dados.linhas || [];
    let html = '';

    linhas.forEach((linha, idx) => {
        const bgRow = idx % 2 === 0 ? '#ffffff' : '#fcf5ff';
        let rowHtml = `<tr style="background:${bgRow};border-bottom:1px solid #e5e7eb;">
            <td style="padding:9px 14px;font-weight:700;color:var(--purple-main);border-right:2px solid #e5e7eb;white-space:nowrap;">${linha.faixa || '-'}</td>`;

        meses.forEach(mes => {
            const val = linha[mes] || 0;
            const cor = val > 0 ? '#6b21a8' : '#9ca3af';
            rowHtml += `<td style="padding:9px 12px;text-align:center;color:${cor};font-weight:${val > 0 ? '600' : '400'};">${val > 0 ? formatarMoeda(val) : '—'}</td>`;
        });

        const totalAno = linha.total_ano || 0;
        rowHtml += `<td style="padding:9px 12px;text-align:center;font-weight:800;color:#6b21a8;background:#f3e8ff;">${formatarMoeda(totalAno)}</td>`;
        rowHtml += '</tr>';
        html += rowHtml;
    });

    // Linha de totais
    if (dados.totais) {
        const t = dados.totais;
        let totalRowHtml = `<tr class="tr-total-row" style="background:var(--purple-main);color:#ffffff;font-weight:800;">
            <td style="padding:10px 14px;border-right:2px solid #581c87;color:#ffffff;background:var(--purple-main);">TOTAL</td>`;
        meses.forEach(mes => {
            const val = t[mes] || 0;
            totalRowHtml += `<td style="padding:10px 12px;text-align:center;color:#ffffff;background:var(--purple-main);">${val > 0 ? formatarMoeda(val) : '—'}</td>`;
        });
        totalRowHtml += `<td class="td-total-sum" style="padding:10px 12px;text-align:center;background:#581c87;color:#ffffff;">${formatarMoeda(t.total_ano || 0)}</td>`;
        totalRowHtml += '</tr>';
        html += totalRowHtml;
    }

    tbody.innerHTML = html;
}

// ================================================================
// RENDERIZAÇÃO - PAGAMENTOS
// ================================================================

function renderizarPagamentos(pagamentos) {
    const tbody = document.getElementById('tabela-pagamentos');
    if (!tbody) return;
    
    if (!pagamentos || pagamentos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#6B7280;padding:30px;">Nenhum pagamento encontrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = pagamentos.slice(0, 10).map(p => `
        <tr>
            <td class="sticky-col-1"><strong>${p.contrato || '-'}</strong></td>
            <td class="sticky-col-3">${p.cliente || '-'}</td>
            <td style="text-align:center;font-weight:600;">${formatarMoeda(p.valorTotal || 0)}</td>
            <td style="text-align:center;">${formatarData(p.dtPgto)}</td>
            <td style="text-align:center;">${renderizarStatus(p.faseAtraso)}</td>
        </tr>
    `).join('');
    
    const badge = document.getElementById('badgePagamentos');
    if (badge) {
        badge.textContent = pagamentos.length;
    }
}

// ================================================================
// RENDERIZAÇÃO - METAS
// ================================================================

function renderizarMetas(metas) {
    const tbody = document.getElementById('tabela-metas');
    if (!tbody) return;
    
    if (!metas || metas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#6B7280;padding:30px;">Nenhuma meta encontrada</td></tr>';
        return;
    }
    
    // Ordena por data
    metas.sort((a, b) => {
        const da = new Date(a.data);
        const db = new Date(b.data);
        return da - db;
    });
    
    tbody.innerHTML = metas.map(m => {
        const data = m.data ? new Date(m.data) : null;
        const mesAno = data ? `${data.toLocaleString('pt-BR', { month: 'long' })}/${data.getFullYear()}` : '—';
        
        const atingidoVal = m.atingido || 0;
        const meta100Val = m.meta100 || 0;
        const perc = meta100Val > 0 ? (atingidoVal / meta100Val) * 100 : 0;
        
        const progressoHtml = m.atingido ? `
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;padding:4px 0;">
                <span style="font-weight:700;color:var(--text-main);">${formatarMoeda(atingidoVal)}</span>
                <div class="table-progress-container" style="min-width:110px;">
                    <div class="table-progress-bar" style="height:6px;">
                        <div class="table-progress-fill purple" style="width: ${Math.min(perc, 100)}%;"></div>
                    </div>
                    <span style="font-size:10px;font-weight:700;color:var(--purple-main);">${perc.toFixed(1)}%</span>
                </div>
            </div>
        ` : '—';

        return `
            <tr>
                <td>${mesAno}</td>
                <td>${formatarMoeda(m.meta70 || 0)}</td>
                <td>${formatarMoeda(m.meta80 || 0)}</td>
                <td>${formatarMoeda(m.meta90 || 0)}</td>
                <td><strong>${formatarMoeda(m.meta100 || 0)}</strong></td>
                <td style="text-align:center;">${progressoHtml}</td>
            </tr>
        `;
    }).join('');
}

// ================================================================
// RENDERIZAÇÃO - EVOLUÇÃO
// ================================================================

function renderizarEvolucao(dados) {
    const container = document.getElementById('resumo-evolucao');
    if (!container) return;
    
    const indicadores = dados.indicadores || {};
    const indicadoresAnt = dados.indicadores_anterior || {};
    
    const fat = indicadores.faturamento_total || 0;
    const fatAnt = indicadoresAnt.faturamento_total || 0;
    const variacao = fatAnt > 0 ? ((fat - fatAnt) / fatAnt) * 100 : 0;
    const diferenca = fat - fatAnt;
    const sinal = diferenca >= 0 ? '+' : '';
    
    container.innerHTML = `
        <div class="evolucao-resumo" style="background: ${diferenca >= 0 ? '#d1fae5' : '#fee2e2'}; color: ${diferenca >= 0 ? '#065f46' : '#991b1b'}; padding: 12px 16px; border-radius: 8px; font-weight: 600;">
            <strong>Variação vs Mês Anterior:</strong>
            ${formatarMoeda(diferenca)} (${sinal}${variacao.toFixed(1)}%)
        </div>
    `;
}

// ================================================================
// RENDERIZAÇÃO - PAGAMENTOS COMPLETOS (com filtros)
// ================================================================

let pagamentosCompletos = [];

function renderizarPagamentosCompletos(pagamentos) {
    const tbody = document.getElementById('tabela-pagamentos-full');
    if (!tbody) return;
    
    pagamentosCompletos = pagamentos || [];
    aplicarFiltroPagamentos();
}

/**
 * Atualiza os 3 cards de resumo (Faturamento, Qtd, Ticket) na página de Pagamentos.
 * @param {Array} lista - Lista de pagamentos filtrados para calcular os totais.
 */
function _atualizarResumoPagOp(lista) {
    const totalFat = lista.reduce((s, p) => s + (parseFloat(p.valorTotal) || 0), 0);
    const totalQtd = lista.length;
    const ticket = totalQtd > 0 ? totalFat / totalQtd : 0;
    const elFat = document.getElementById('pag-op-resumo-faturamento');
    const elQtd = document.getElementById('pag-op-resumo-qtd');
    const elTkt = document.getElementById('pag-op-resumo-ticket');
    if (elFat) elFat.textContent = formatarMoeda(totalFat);
    if (elQtd) elQtd.textContent = totalQtd;
    if (elTkt) elTkt.textContent = formatarMoeda(ticket);
}

let pagamentosCompletosFiltrados = [];
let pagCompletosPage = 1;
const pagCompletosPerPage = 50;

function aplicarFiltroPagamentos() {
    const tbody = document.getElementById('tabela-pagamentos-full');
    const totalRegistros = document.getElementById('total-registros') || document.getElementById('pag-op-total-reg');
    if (!tbody) return;
    
    const busca = document.getElementById('filtro-pagamento-busca');
    const fase = document.getElementById('filtro-pagamento-fase');
    const inicioInput = document.getElementById('filtro-pagamento-inicio');
    const fimInput = document.getElementById('filtro-pagamento-fim');

    const buscaText = busca ? busca.value.toLowerCase() : '';
    const faseText = fase ? fase.value : '';
    const inicioVal = inicioInput ? inicioInput.value : '';
    const fimVal = fimInput ? fimInput.value : '';

    let filtrados = pagamentosCompletos;

    // NOTA: NÃO refiltramos por mês/ano aqui de propósito.
    // `pagamentosCompletos` já vem do servidor filtrado exatamente para o
    // mês/ano selecionado (ver /api/resumo -> ultimos_pagamentos). Refiltrar
    // de novo no navegador usando os dropdowns filtro-pagamento-mes/ano
    // causava um bug real: esses dropdowns podiam ficar dessincronizados
    // dos filtros filtro-mes/filtro-ano do dashboard principal (ex: usuário
    // troca o mês na aba Dashboard, os dados certos chegam do servidor, mas
    // aqui filtrava de novo com o mês antigo e sumia/errava os registros).
    // Range de datas (início/fim) continua funcionando normalmente abaixo.

    if (buscaText) {
        filtrados = filtrados.filter(p => 
            (p.cliente || '').toLowerCase().includes(buscaText) ||
            (p.contrato || '').toLowerCase().includes(buscaText)
        );
    }
    
    if (faseText) {
        filtrados = filtrados.filter(p => (p.faseAtraso || '') === faseText);
    }

    if (inicioVal) {
        filtrados = filtrados.filter(p => p.dtPgto >= inicioVal);
    }

    if (fimVal) {
        filtrados = filtrados.filter(p => p.dtPgto <= fimVal);
    }
    
    pagamentosCompletosFiltrados = filtrados;
    pagCompletosPage = 1;
    renderizarTabelaPagamentosOpPaginada();

    // Sempre atualiza os cards de resumo da página de Pagamentos
    _atualizarResumoPagOp(filtrados);

    // Atualiza os cards do Dashboard (kpi-faturamento etc.) se houver filtro de data ativo
    const temFiltroData = (inicioVal || fimVal);
    if (temFiltroData) {
        const totalFat = filtrados.reduce((s, p) => s + (parseFloat(p.valorTotal) || 0), 0);
        const totalQtd = filtrados.length;
        const ticket = totalQtd > 0 ? totalFat / totalQtd : 0;
        const elFat = document.getElementById('kpi-faturamento');
        const elQtd = document.getElementById('kpi-total-pgtos');
        const elTkt = document.getElementById('kpi-ticket');
        if (elFat) elFat.textContent = formatarMoeda(totalFat);
        if (elQtd) elQtd.textContent = totalQtd;
        if (elTkt) elTkt.textContent = formatarMoeda(ticket);
    } else {
        // Sem filtro de data: restaura os valores originais do servidor
        if (window.dadosCompletos) {
            const ind = window.dadosCompletos.indicadores || {};
            const elFat = document.getElementById('kpi-faturamento');
            const elQtd = document.getElementById('kpi-total-pgtos');
            const elTkt = document.getElementById('kpi-ticket');
            if (elFat) elFat.textContent = formatarMoeda(ind.faturamento_total || 0);
            if (elQtd) elQtd.textContent = ind.total_pagamentos || 0;
            if (elTkt) elTkt.textContent = formatarMoeda(ind.ticket_medio || 0);
        }
    }
}

function renderizarTabelaPagamentosOpPaginada() {
    const tbody = document.getElementById('tabela-pagamentos-full');
    const totalRegistros = document.getElementById('total-registros');
    const pagEl = document.getElementById('pag-op-completos-pagination');
    if (!tbody || !totalRegistros) return;

    // "Fase Atraso" só faz sentido para SEMEAR (item 13)
    const banco = (window.operadorLogado && window.operadorLogado.banco) || 'SEMEAR';
    const mostrarFase = banco !== 'AGORACRED';
    const thFase = document.getElementById('th-pagamentos-full-fase');
    if (thFase) thFase.style.display = mostrarFase ? '' : 'none';
    const totalColunas = mostrarFase ? 5 : 4;

    const total = pagamentosCompletosFiltrados.length;
    totalRegistros.textContent = `${total} registros`;

    const totalPages = Math.max(1, Math.ceil(total / pagCompletosPerPage));
    pagCompletosPage = Math.min(pagCompletosPage, totalPages);

    const inicio = (pagCompletosPage - 1) * pagCompletosPerPage;
    const pagina = pagamentosCompletosFiltrados.slice(inicio, inicio + pagCompletosPerPage);

    if (pagina.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${totalColunas}" style="text-align:center;color:#6B7280;padding:30px;">Nenhum pagamento encontrado</td></tr>`;
        if (pagEl) pagEl.innerHTML = '';
        return;
    }

    const totalFaturamento = pagamentosCompletosFiltrados.reduce((sum, p) => sum + (p.valorTotal || 0), 0);

    tbody.innerHTML = pagina.map(p => `
        <tr>
            <td style="text-align:center;font-size:12px;">${formatarData(p.dtPgto)}</td>
            <td style="text-align:center;"><strong>${p.contrato || '-'}</strong></td>
            <td style="text-align:left;">${p.cliente || '-'}</td>
            <td style="text-align:center;font-weight:600;color:var(--purple-main);">${formatarMoeda(p.valorTotal || 0)}</td>
            ${mostrarFase ? `<td style="text-align:center;">${p.faseAtraso || '-'}</td>` : ''}
        </tr>
    `).join('') + `
        <tr class="sticky-total-row">
            <td colspan="3" style="text-align:right;font-weight:700;"><i class="fas fa-sigma"></i> TOTAL FILTRADO</td>
            <td style="text-align:center;font-weight:700;color:var(--purple-main);">${formatarMoeda(totalFaturamento)}</td>
            ${mostrarFase ? '<td>-</td>' : ''}
        </tr>
    `;

    // Renderiza paginação
    if (pagEl) {
        if (totalPages <= 1) { pagEl.innerHTML = ''; return; }
        let html = '';
        const prev = pagCompletosPage > 1;
        const next = pagCompletosPage < totalPages;
        html += `<button onclick="pagCompletosIr(${pagCompletosPage-1})" ${prev?'':'disabled'} style="padding:4px 8px;border-radius:6px;border:1px solid #d1d5db;cursor:${prev?'pointer':'not-allowed'};background:${prev?'white':'#f3f4f6'};">‹</button>`;
        
        const start = Math.max(1, pagCompletosPage - 2);
        const end = Math.min(totalPages, pagCompletosPage + 2);
        for (let i = start; i <= end; i++) {
            html += `<button onclick="pagCompletosIr(${i})" style="padding:4px 8px;border-radius:6px;border:1px solid ${i===pagCompletosPage?'var(--purple-main)':'#d1d5db'};background:${i===pagCompletosPage?'var(--purple-main)':'white'};color:${i===pagCompletosPage?'white':'inherit'};font-weight:700;cursor:pointer;">${i}</button>`;
        }
        
        html += `<button onclick="pagCompletosIr(${pagCompletosPage+1})" ${next?'':'disabled'} style="padding:4px 8px;border-radius:6px;border:1px solid #d1d5db;cursor:${next?'pointer':'not-allowed'};background:${next?'white':'#f3f4f6'};">›</button>`;
        pagEl.innerHTML = html;
    }
}

function pagCompletosIr(page) {
    pagCompletosPage = page;
    renderizarTabelaPagamentosOpPaginada();
}

window.pagCompletosIr = pagCompletosIr;

function filtrarPagamentos() {
    aplicarFiltroPagamentos();
}
window.filtrarPagamentos = filtrarPagamentos;

// ================================================================
// TABELAS ADICIONAIS DO DASHBOARD DO OPERADOR
// ================================================================

function renderizarTabelaPerformanceOpNova(perf) {
    const tbody = document.getElementById('tabela-performance-operador-nova');
    if (!tbody) return;

    // Atualiza o banner de última baixa bancária na página inicial do operador
    const bannerEl = document.getElementById('banner-ultima-baixa-operador-nova');
    const txtEl = document.getElementById('txt-ultima-baixa-operador-nova');
    if (bannerEl && txtEl) {
        const ultimaBaixa = perf.ultima_baixa_banco;
        if (ultimaBaixa) {
            // Normaliza para DD/MM/YYYY (pode chegar como 'YYYY-MM-DD' ou 'DD/MM/YYYY')
            let dataFmt = ultimaBaixa;
            if (ultimaBaixa.includes('-')) {
                const partes = ultimaBaixa.split('-');
                dataFmt = `${partes[2].substring(0,2)}/${partes[1]}/${partes[0]}`;
            }
            const duCalculado = typeof calcularDUdaData === 'function' ? calcularDUdaData(dataFmt) : '';
            const tagDu = duCalculado ? ` <span style="background:rgba(255,255,255,0.7);padding:2px 8px;border-radius:6px;font-size:12px;font-weight:700;margin-left:6px;border:1px solid currentColor;">${duCalculado}</span>` : '';
            txtEl.innerHTML = `<strong>Baixas até ${dataFmt}</strong>${tagDu} <span style="color:var(--text-muted);font-weight:400;">(Feito/Dia = Faturamento ÷ ${duCalculado ? duCalculado : parseInt(diaBaixa) + ' dias'})</span>`;
            const isAgoracred = window.operadorLogado?.banco === 'AGORACRED';
            bannerEl.style.background = isAgoracred ? 'linear-gradient(90deg,#10b98120,#34d39910)' : 'linear-gradient(90deg,#7e3d9720,#a855f710)';
            bannerEl.style.borderColor = isAgoracred ? '#10b98140' : '#a855f740';
            bannerEl.querySelector('i').style.color = isAgoracred ? '#10b981' : '#a855f7';
            bannerEl.style.display = 'flex';
        } else {
            bannerEl.style.display = 'none';
        }
    }

    const thead = tbody.previousElementSibling;
    if (thead) {
        thead.style.backgroundColor = (window.operadorLogado?.banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
    }

    if (!perf || Object.keys(perf).length === 0) {
        tbody.innerHTML = '<tr><td colspan="16" style="text-align:center;color:#6B7280;padding:20px;">Nenhum dado disponível</td></tr>';
        return;
    }

    const nomeOp = (window.operadorLogado && window.operadorLogado.nome) || perf.login || 'Operador';
    const imagemOp = window.operadorLogado && window.operadorLogado.imagem;
    const iniciaisOp = getIniciais(nomeOp);
    const fotoHtml = imagemOp
        ? `<img src="${imagemOp}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;">`
        : `<div style="width:32px;height:32px;border-radius:50%;background:var(--purple-main);color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;margin:0 auto;">${iniciaisOp}</div>`;

    tbody.innerHTML = `
        <tr>
            <td style="text-align:center;">${fotoHtml}</td>
            <td style="text-align:center;font-weight:600;color:var(--purple-main);">${perf.login || '-'}</td>
            <td style="text-align:center;">${perf.turno || '-'}</td>
            <td style="text-align:center;font-weight:700;color:var(--purple-main);">${perf.quantidade || 0}</td>
            <td style="text-align:center;font-weight:700;">${formatarMoeda(perf.faturamento || 0)}</td>
            <td style="text-align:center;">${formatarMoeda(perf.feito_diario || 0)}</td>
            <td style="text-align:center;font-weight:700;">${formatarMoeda(perf.meta || 0)}</td>
            <td style="text-align:center;">${formatarMoeda(perf.meta_diaria || 0)}</td>
            <td style="text-align:center;">${criarBarraProgresso(perf.atingido_meta || 0)}</td>
            <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_70 || 0)}</td>
            <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_80 || 0)}</td>
            <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_90 || 0)}</td>
            <td style="text-align:center;color:#7c3aed;font-weight:700;">${formatarMoeda(perf.falta_100 || 0)}</td>
            <td style="text-align:center;font-weight:700;">${perf.ranking || '—'}</td>
            <td style="text-align:center;font-weight:700;color:#0891b2;">${formatarMoeda(perf.projecao || 0)}</td>
            <td style="text-align:center;">${criarBarraProgresso(perf.projecao_percentual || 0)}</td>
        </tr>
    `;

    // Info de dias úteis acima da tabela (quantos já passaram / quantos faltam)
    const infoDiasEl = document.getElementById('perf-dias-info-nova');
    if (infoDiasEl) {
        infoDiasEl.innerHTML = `
            <i class="fas fa-calendar-check" style="color:var(--purple-main);"></i>
            Dias úteis trabalhados: <strong>${perf.dias_trabalhados ?? 0}</strong>
            &nbsp;|&nbsp;
            <i class="fas fa-hourglass-half" style="color:#0891b2;"></i>
            Dias úteis restantes: <strong>${perf.dias_restantes ?? 0}</strong>
            &nbsp;|&nbsp;
            <i class="fas fa-calendar" style="color:#7c3aed;"></i>
            Total de dias úteis no mês: <strong>${perf.total_dias_uteis ?? 0}</strong>
        `;
    }
}

function renderizarTabelaResultadoMesAMesNova(lista) {
    const tbody = document.getElementById('tabela-resultado-mes-a-mes');
    if (!tbody) return;

    if (!lista || lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#6B7280;padding:20px;">Nenhum histórico disponível</td></tr>';
        return;
    }

    // Calcula variação vs mês anterior usando a lista completa (cronológica),
    // mas só exibe os meses que de fato têm meta definida (item 4)
    const comVariacao = lista.map((item, idx) => {
        const anterior = idx > 0 ? lista[idx - 1] : null;
        const fatAnt = anterior ? (anterior.faturamento || 0) : null;
        let variacaoPct = null;
        let variacaoDif = null;
        if (fatAnt !== null && fatAnt > 0) {
            variacaoDif = (item.faturamento || 0) - fatAnt;
            variacaoPct = (variacaoDif / fatAnt) * 100;
        }
        return { ...item, variacaoPct, variacaoDif };
    });

    const comMeta = comVariacao.filter(item => (item.meta || 0) > 0);

    if (comMeta.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#6B7280;padding:20px;">Nenhum mês com meta definida no período</td></tr>';
        return;
    }

    tbody.innerHTML = comMeta.map(item => {
        const bateuCor = item.bateu === 'Sim' ? '#16a34a' : '#dc2626';
        const bateuBg = item.bateu === 'Sim' ? '#dcfce7' : '#fee2e2';
        const varHtml = item.variacaoPct === null
            ? '<span style="color:#9ca3af;">—</span>'
            : `<span style="color:${item.variacaoPct >= 0 ? '#16a34a' : '#dc2626'};font-weight:700;">${item.variacaoPct >= 0 ? '▲' : '▼'} ${Math.abs(item.variacaoPct).toFixed(1)}%</span>`;
        return `
            <tr>
                <td style="text-align:center;font-weight:600;">${item.mes}</td>
                <td style="text-align:center;">${item.quantidade}</td>
                <td style="text-align:center;font-weight:600;">${formatarMoeda(item.faturamento)}</td>
                <td style="text-align:center;">${formatarMoeda(item.meta)}</td>
                <td style="text-align:center;font-weight:600;">${item.perc_meta.toFixed(1)}%</td>
                <td style="text-align:center;">${varHtml}</td>
                <td style="text-align:center;">
                    <span style="background:${bateuBg};color:${bateuCor};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;">${item.bateu}</span>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarPagamentosRecentesPaginados() {
    const tbody = document.getElementById('tabela-pagamentos-recentes-paginada');
    const totalEl = document.getElementById('pag-op-total-registros');
    const pagEl = document.getElementById('pag-op-recentes-pagination');
    const thFase = document.getElementById('th-recentes-fase');
    if (!tbody) return;

    const banco = (window.operadorLogado && window.operadorLogado.banco) || 'SEMEAR';
    const mostrarFase = banco !== 'AGORACRED';
    if (thFase) thFase.style.display = mostrarFase ? '' : 'none';

    const dadosBase = pagamentosRecentesOpFiltrados || pagamentosRecentesOpData;

    if (totalEl) totalEl.textContent = `${dadosBase.length} registros`;

    const total = dadosBase.length;
    const totalPages = Math.max(1, Math.ceil(total / pagRecentesOpPerPage));
    pagRecentesOpPage = Math.min(pagRecentesOpPage, totalPages);

    const inicio = (pagRecentesOpPage - 1) * pagRecentesOpPerPage;
    const pagina = dadosBase.slice(inicio, inicio + pagRecentesOpPerPage);

    if (pagina.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${mostrarFase ? 5 : 4}" style="text-align:center;color:#6B7280;padding:20px;">Nenhum pagamento encontrado.</td></tr>`;
        if (pagEl) pagEl.innerHTML = '';
        return;
    }

    tbody.innerHTML = pagina.map(p => `
        <tr>
            <td style="text-align:center;font-size:12px;">${formatarData(p.dtPgto)}</td>
            <td style="text-align:center;font-weight:600;">${p.contrato || '-'}</td>
            <td style="text-align:left;">${p.cliente || '-'}</td>
            <td style="text-align:center;font-weight:700;color:var(--purple-main);">${formatarMoeda(p.valorTotal || 0)}</td>
            ${mostrarFase ? `<td style="text-align:center;">${renderizarStatus(p.faseAtraso)}</td>` : ''}
        </tr>
    `).join('');

    // Renderiza botões de paginação
    if (pagEl) {
        if (totalPages <= 1) { pagEl.innerHTML = ''; return; }
        let html = '';
        const prev = pagRecentesOpPage > 1;
        const next = pagRecentesOpPage < totalPages;
        html += `<button onclick="opRecentesIr(${pagRecentesOpPage-1})" ${prev?'':'disabled'} style="padding:4px 8px;border-radius:6px;border:1px solid #d1d5db;cursor:${prev?'pointer':'not-allowed'};background:${prev?'white':'#f3f4f6'};">‹</button>`;
        for (let i = 1; i <= totalPages; i++) {
            html += `<button onclick="opRecentesIr(${i})" style="padding:4px 8px;border-radius:6px;border:1px solid ${i===pagRecentesOpPage?'var(--purple-main)':'#d1d5db'};background:${i===pagRecentesOpPage?'var(--purple-main)':'white'};color:${i===pagRecentesOpPage?'white':'inherit'};font-weight:700;cursor:pointer;">${i}</button>`;
        }
        html += `<button onclick="opRecentesIr(${pagRecentesOpPage+1})" ${next?'':'disabled'} style="padding:4px 8px;border-radius:6px;border:1px solid #d1d5db;cursor:${next?'pointer':'not-allowed'};background:${next?'white':'#f3f4f6'};">›</button>`;
        pagEl.innerHTML = html;
    }
}

function opRecentesIr(page) {
    pagRecentesOpPage = page;
    renderizarPagamentosRecentesPaginados();
}

window.opRecentesIr = opRecentesIr;

// ================================================================
// DETALHE DA PERFORMANCE DO OPERADOR (PÁGINA OPERADORES)
// ================================================================

function renderizarMinhaPerformanceOp(dadosPerformance) {
    if (!dadosPerformance) return;

    const perf = dadosPerformance.performance || {};
    
    // Atualiza o banner de última baixa bancária na aba Minha Performance
    const bannerElAba = document.getElementById('banner-ultima-baixa-operador-aba');
    const txtElAba = document.getElementById('txt-ultima-baixa-operador-aba');
    if (bannerElAba && txtElAba) {
        const ultimaBaixa = perf.ultima_baixa_banco;
        if (ultimaBaixa) {
            // Normaliza para DD/MM/YYYY (pode chegar como 'YYYY-MM-DD' ou 'DD/MM/YYYY')
            let dataFmtAba = ultimaBaixa;
            if (ultimaBaixa.includes('-')) {
                const partes = ultimaBaixa.split('-');
                dataFmtAba = `${partes[2].substring(0,2)}/${partes[1]}/${partes[0]}`;
            }
            const duCalculadoAba = typeof calcularDUdaData === 'function' ? calcularDUdaData(dataFmtAba) : '';
            const tagDuAba = duCalculadoAba ? ` <span style="background:rgba(255,255,255,0.7);padding:2px 8px;border-radius:6px;font-size:12px;font-weight:700;margin-left:6px;border:1px solid currentColor;">${duCalculadoAba}</span>` : '';
            txtElAba.innerHTML = `<strong>Baixas até ${dataFmtAba}</strong>${tagDuAba} <span style="color:var(--text-muted);font-weight:400;">(Feito/Dia = Faturamento ÷ ${duCalculadoAba ? duCalculadoAba : parseInt(diaBaixaAba) + ' dias'})</span>`;
            const isAgoracred = window.operadorLogado?.banco === 'AGORACRED';
            bannerElAba.style.background = isAgoracred ? 'linear-gradient(90deg,#10b98120,#34d39910)' : 'linear-gradient(90deg,#7e3d9720,#a855f710)';
            bannerElAba.style.borderColor = isAgoracred ? '#10b98140' : '#a855f740';
            bannerElAba.querySelector('i').style.color = isAgoracred ? '#10b981' : '#a855f7';
            bannerElAba.style.display = 'flex';
        } else {
            bannerElAba.style.display = 'none';
        }
    }

    const diarios = dadosPerformance.performance_diaria || [];
    // Usa indicadores_anterior que vem junto com os dados (fix variação de mês)
    const indAnt = dadosPerformance.indicadores_anterior || window.dadosCompletos?.indicadores_anterior || {};
    // TMA que vem com os dados completos
    const tmaData = dadosPerformance.tma || {};

    // --- TMA (Métricas de Ligação) ---
    if (Object.keys(tmaData).length > 0) {
        const tmaEl = document.getElementById('kpi-tma-valor');
        const tmafEl = document.getElementById('kpi-tma-falado');
        const acionEl = document.getElementById('kpi-tma-acionamentos');
        const ultEl = document.getElementById('kpi-tma-ultimo');
        const reacEl = document.getElementById('kpi-tma-reacionamento');
        const cliEl = document.getElementById('kpi-tma-clientes');
        if (tmaEl) tmaEl.textContent = tmaData.tma || '00:00:00';
        if (tmafEl) tmafEl.innerHTML = `Falado no mês: <strong>${tmaData.tempo_falado || '0h 00min'}</strong>`;
        if (acionEl) acionEl.textContent = tmaData.acionamentos || 0;
        if (ultEl) ultEl.innerHTML = `Últ. Acion.: <strong>${_formatarDataAcionamento(tmaData.ultimo_acionamento)}</strong>`;
        if (reacEl) reacEl.textContent = tmaData.reacionamento || '1.00';
        if (cliEl) cliEl.innerHTML = `Clientes únicos: <strong>${tmaData.clientes || 0}</strong>`;
    }

    // --- 1. RENDERIZAR PERFORMANCE NA ABA DE PERFORMANCE ---
    const tbodyPerf = document.getElementById('tabela-performance-operador-aba');
    if (tbodyPerf) {
        const theadPerf = tbodyPerf.previousElementSibling;
        if (theadPerf) {
            theadPerf.style.backgroundColor = (window.operadorLogado?.banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
        }
        const nomeOpPerf = (window.operadorLogado && window.operadorLogado.nome) || perf.login || 'Operador';
        const imagemOpPerf = window.operadorLogado && window.operadorLogado.imagem;
        const iniciaisOpPerf = getIniciais(nomeOpPerf);
        const fotoHtmlPerf = imagemOpPerf
            ? `<img src="${imagemOpPerf}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;">`
            : `<div style="width:32px;height:32px;border-radius:50%;background:var(--purple-main);color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;margin:0 auto;">${iniciaisOpPerf}</div>`;

        tbodyPerf.innerHTML = `
            <tr>
                <td style="text-align:center;">${fotoHtmlPerf}</td>
                <td style="text-align:center;font-weight:600;color:var(--purple-main);">${perf.login || '-'}</td>
                <td style="text-align:center;font-weight:700;color:var(--purple-main);">${perf.quantidade || 0}</td>
                <td style="text-align:center;font-weight:700;">${formatarMoeda(perf.faturamento || 0)}</td>
                <td style="text-align:center;">${formatarMoeda(perf.feito_diario || 0)}</td>
                <td style="text-align:center;font-weight:700;">${formatarMoeda(perf.meta || 0)}</td>
                <td style="text-align:center;">${criarBarraProgresso(perf.atingido_meta || 0)}</td>
                <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_70 || 0)}</td>
                <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_80 || 0)}</td>
                <td style="text-align:center;color:#dc2626;">${formatarMoeda(perf.falta_90 || 0)}</td>
                <td style="text-align:center;color:#7c3aed;font-weight:700;">${formatarMoeda(perf.falta_100 || 0)}</td>
                <td style="text-align:center;font-weight:700;">${perf.ranking || '—'}</td>
                <td style="text-align:center;font-weight:700;color:#0891b2;">${formatarMoeda(perf.projecao || 0)}</td>
                <td style="text-align:center;">${criarBarraProgresso(perf.projecao_percentual || 0)}</td>
            </tr>
        `;

        // Info de dias úteis acima da tabela
        const infoDiasElAba = document.getElementById('perf-dias-info-aba');
        if (infoDiasElAba) {
            infoDiasElAba.innerHTML = `
                <i class="fas fa-calendar-check" style="color:var(--purple-main);"></i>
                Dias úteis trabalhados: <strong>${perf.dias_trabalhados ?? 0}</strong>
                &nbsp;|&nbsp;
                <i class="fas fa-hourglass-half" style="color:#0891b2;"></i>
                Dias úteis restantes: <strong>${perf.dias_restantes ?? 0}</strong>
                &nbsp;|&nbsp;
                <i class="fas fa-calendar" style="color:#7c3aed;"></i>
                Total de dias úteis no mês: <strong>${perf.total_dias_uteis ?? 0}</strong>
            `;
        }
    }

    // --- 2. RESUMO DOS DIAS ---
    let diasComMeta = 0;
    let diasSemMeta = 0;
    diarios.forEach(d => {
        if (d.meta_batida && d.meta_batida.includes('Sim')) diasComMeta++;
        else if (d.meta_batida && d.meta_batida.includes('Não')) diasSemMeta++;
    });

    document.getElementById('op-dias-trab').textContent = perf.dias_trabalhados || 0;
    document.getElementById('op-dias-com-meta').textContent = diasComMeta;
    document.getElementById('op-dias-sem-meta').textContent = diasSemMeta;
    document.getElementById('op-dias-rest').textContent = perf.dias_restantes || 0;
    document.getElementById('op-total-dias').textContent = perf.total_dias_uteis || 0;

    // --- ALERTA DE INATIVIDADE (> 2 DIAS) ---
    const modalAlerta = document.getElementById('alerta-sem-pgto-modal');
    if (modalAlerta) {
        if (perf && perf.alerta_sem_pgto) {
            modalAlerta.style.display = 'block';
            const txtSub = document.getElementById('alerta-sem-pgto-sub');
            if (txtSub) txtSub.textContent = `Você está há ${perf.dias_sem_pgto} dias sem registrar recebimentos nesta carteira.`;
        } else {
            modalAlerta.style.display = 'none';
        }
    }

    // --- 3. RECEBIMENTO DIÁRIO ---
    const tbodyDiario = document.getElementById('tabela-recebimento-diario-op');
    if (tbodyDiario) {
        const theadDiario = tbodyDiario.previousElementSibling;
        if (theadDiario) {
            theadDiario.style.backgroundColor = (window.operadorLogado?.banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
        }
        if (diarios.length === 0) {
            tbodyDiario.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#6B7280;padding:20px;">Nenhum faturamento registrado nos dias úteis.</td></tr>';
        } else {
            tbodyDiario.innerHTML = diarios.map((d) => {
                const dataExib = d.data_formatada || d.data || '—';
                const duExib = d.dia_util || '—';
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

    // --- 3.1. VISÃO TRIMESTRAL POR DIA ÚTIL ---
    if (typeof renderizarTrimestreDUOp === 'function') {
        renderizarTrimestreDUOp(dadosPerformance.trimestre_du);
    }
    // Guarda referência dos dados de performance
    window._ultimoResultadoPerformance = dadosPerformance;

    // --- 4. FATURAMENTO POR SEMANA ---
    renderizarSemanalOp();


    // --- 5. RESULTADO MÊS A MÊS ---
    const tbodyMesAPerf = document.getElementById('tabela-resultado-mes-a-mes-perf');
    const listaResultadoMes = (dadosPerformance && dadosPerformance.resultado_mes_a_mes) || (window.dadosCompletos && window.dadosCompletos.resultado_mes_a_mes) || [];
    if (tbodyMesAPerf && listaResultadoMes.length > 0) {
        const isAgora = window.operadorLogado?.banco === 'AGORACRED';
        const mainColor = isAgora ? 'var(--emerald)' : 'var(--purple-main)';
        const projHeaderColor = isAgora ? '#047857' : '#5b21b6';
        const projCellBg = isAgora ? '#d1fae5' : '#f3e8ff';
        const projMoneyColor = isAgora ? '#047857' : '#5b21b6';

        const theadMesA = tbodyMesAPerf.previousElementSibling;
        if (theadMesA) {
            theadMesA.style.backgroundColor = mainColor;
            const thVal = document.getElementById('th-projecao-val');
            const thPct = document.getElementById('th-projecao-pct');
            if (thVal) thVal.style.backgroundColor = projHeaderColor;
            if (thPct) thPct.style.backgroundColor = projHeaderColor;
        }

        const comVariacao = listaResultadoMes.map((item, idx) => {
            const anterior = idx > 0 ? listaResultadoMes[idx - 1] : null;
            const fatAnt = anterior ? (anterior.faturamento || 0) : null;
            let variacaoPct = null;
            if (fatAnt !== null && fatAnt > 0) {
                variacaoPct = (((item.faturamento || 0) - fatAnt) / fatAnt) * 100;
            }
            return { ...item, variacaoPct };
        });
        const comDados = comVariacao.filter(item => (item.faturamento || 0) > 0 || (item.meta || 0) > 0);

        if (comDados.length === 0) {
            tbodyMesAPerf.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#6B7280;padding:20px;">Nenhum mês com histórico no período</td></tr>';
        } else {
            tbodyMesAPerf.innerHTML = comDados.map(item => {
                const bateuCor = item.bateu === 'Sim' ? '#16a34a' : '#dc2626';
                const bateuBg = item.bateu === 'Sim' ? '#dcfce7' : '#fee2e2';
                const varHtml = item.variacaoPct === null
                    ? '<span style="color:#9ca3af;">—</span>'
                    : `<span style="color:${item.variacaoPct >= 0 ? '#16a34a' : '#dc2626'};font-weight:700;">${item.variacaoPct >= 0 ? '▲' : '▼'} ${Math.abs(item.variacaoPct).toFixed(1)}%</span>`;

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
                    <tr>
                        <td style="text-align:center;font-weight:600;">${item.mes}</td>
                        <td style="text-align:center;">${item.quantidade}</td>
                        <td style="text-align:center;font-weight:600;">${formatarMoeda(item.faturamento)}</td>
                        <td style="text-align:center;">${formatarMoeda(item.meta)}</td>
                        <td style="text-align:center;font-weight:600;">${(item.perc_meta || 0).toFixed(1)}%</td>
                        <td style="text-align:center;">${varHtml}</td>
                        <td style="text-align:center;">
                            <span style="background:${bateuBg};color:${bateuCor};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;">${item.bateu}</span>
                        </td>
                        <td style="text-align:center;background:${projCellBg};">${projHtml}</td>
                        <td style="text-align:center;background:${projCellBg};">${projPctHtml}</td>
                    </tr>
                `;
            }).join('');
        }
    }


    // --- 6. VARIAÇÃO VS MÊS ANTERIOR ---
    const divVar = document.getElementById('op-variacao-periodo-detalhe');
    if (divVar) {
        const fatMes = perf.faturamento || 0;
        // Usa indicadores_anterior do próprio payload (não do estado global)
        const fatAnt = indAnt.faturamento_total || 0;
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

    // --- 6b. TABELA DETALHADA DE VARIAÇÃO ---
    const listaVariacao = (dadosPerformance.resultado_mes_a_mes && dadosPerformance.resultado_mes_a_mes.length > 0)
        ? dadosPerformance.resultado_mes_a_mes
        : ((window.dadosCompletos && window.dadosCompletos.resultado_mes_a_mes) || []);
    renderizarVariacaoDetalhada(listaVariacao);

    // --- 7. GRÁFICOS ---
    renderizarGraficoBarrasMensalOp();
}

function renderizarSemanalOp() {
    const tbody = document.getElementById('tabela-faturamento-semanal-op');
    if (!tbody) return;

    const theadSemanal = tbody.previousElementSibling;
    if (theadSemanal) {
        theadSemanal.style.backgroundColor = (window.operadorLogado?.banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
    }

    const pagamentos = (window.dadosCompletos && window.dadosCompletos.ultimos_pagamentos) || pagamentosRecentesOpData || [];
    if (!pagamentos || pagamentos.length === 0) {
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

    pagamentos.forEach(p => {
        if (!p.dtPgto) return;
        let dia = NaN;
        const s = String(p.dtPgto).trim();
        if (s.includes('/')) {
            dia = parseInt(s.split('/')[0], 10);
        } else if (s.includes('-')) {
            const parts = s.split('-');
            dia = parseInt(parts[2] ? parts[2].substring(0, 2) : parts[0], 10);
        }
        if (isNaN(dia)) return;

        for (let sem of semanas) {
            if (dia >= sem.inicio && dia <= sem.fim) {
                sem.total += parseFloat(p.valorTotal) || 0;
                sem.qtd++;
                break;
            }
        }
    });

    tbody.innerHTML = semanas.map(s => {
        const mes = getMesAtual() < 10 ? '0' + getMesAtual() : getMesAtual();
        const pd = `${s.inicio < 10 ? '0' + s.inicio : s.inicio}/${mes} a ${s.fim}/${mes}`;
        const corTotal = (window.operadorLogado?.banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
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

let chartMensalOp = null;

function renderizarGraficoBarrasMensalOp() {
    const el = document.getElementById('grafico-barras-faturamento-mensal');
    if (!el) return;

    const lista = (window._ultimoResultadoPerformance && window._ultimoResultadoPerformance.resultado_mes_a_mes)
        || (window.dadosCompletos && window.dadosCompletos.resultado_mes_a_mes) || [];

    const listaComDados = lista.filter(m => (m.faturamento || 0) > 0 || (m.meta || 0) > 0);
    if (!listaComDados || listaComDados.length === 0) return;

    const meses = listaComDados.map(m => {
        const nome = m.mes_nome || m.mes || '';
        return typeof nome === 'string' ? nome.substring(0, 3) : String(nome);
    });
    const faturamentos = listaComDados.map(m => m.faturamento || 0);

    const maxVal = Math.max(...faturamentos, 100);

    const options = {
        series: [{
            name: 'Faturamento',
            data: faturamentos
        }],
        chart: {
            type: 'bar',
            height: 190,
            toolbar: { show: false }
        },
        colors: [window.operadorLogado?.banco === 'AGORACRED' ? '#10B981' : '#7e3d97'],
        plotOptions: {
            bar: {
                borderRadius: 4,
                columnWidth: '55%',
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
            style: { fontSize: '11px', fontWeight: '700', colors: [window.operadorLogado?.banco === 'AGORACRED' ? '#047857' : '#6b21a8'] },
            offsetY: -22
        },
        grid: { padding: { top: 25 } },
        xaxis: {
            categories: meses
        },
        yaxis: {
            max: maxVal * 1.25,
            labels: {
                formatter: (v) => formatarMoeda(v)
            }
        }
    };

    if (chartMensalOp) {
        chartMensalOp.destroy();
    }

    chartMensalOp = new ApexCharts(el, options);
    chartMensalOp.render();
}

function renderizarVariacaoDetalhada(lista) {
    const tbody = document.getElementById('tabela-variacao-detalhada-op');
    if (!tbody) return;

    const theadVar = tbody.previousElementSibling;
    if (theadVar) {
        theadVar.style.backgroundColor = (window.operadorLogado?.banco === 'AGORACRED') ? 'var(--emerald)' : 'var(--purple-main)';
    }

    if (!lista || lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#6B7280;padding:20px;">Nenhum histórico disponível</td></tr>';
        return;
    }

    const comDados = lista.filter(item => (item.faturamento || 0) > 0 || (item.meta || 0) > 0);

    if (comDados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#6B7280;padding:20px;">Nenhum mês com histórico no período</td></tr>';
        return;
    }

    let prevFat = null;
    let prevPerc = null;

    tbody.innerHTML = comDados.map((item, idx) => {
        const varR = prevFat !== null ? (item.faturamento - prevFat) : 0;
        const varPct = prevFat !== null && prevFat > 0 ? ((item.faturamento - prevFat) / prevFat) * 100 : 0;
        const varMeta = prevPerc !== null ? (item.perc_meta - prevPerc) : 0;

        const corVar = varR >= 0 ? '#16a34a' : '#dc2626';
        const setaVar = varR >= 0 ? '<i class="fas fa-arrow-up"></i>' : '<i class="fas fa-arrow-down"></i>';

        // Suporte a diferentes nomes de campo (mes_nome, periodo, mes)
        const nomeMes = item.mes_nome || item.periodo || item.mes || '';
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

window.renderizarMinhaPerformanceOp = renderizarMinhaPerformanceOp;

// ================================================================
// UTILITÁRIOS DE DATA
// ================================================================

/**
 * Formata uma data de acionamento do formato ISO americano para pt-BR.
 * Ex: "2026-07-07 09:21:36" → "07/07/2026 09:21"
 * Ex: "2026-07-07" → "07/07/2026"
 * Retorna '—' se o valor for nulo/inválido.
 */
function _formatarDataAcionamento(valor) {
    if (!valor || valor === '-' || valor === 'nan') return '—';
    try {
        // Tenta criar o objeto Date a partir da string
        const dt = new Date(valor.replace(' ', 'T'));
        if (isNaN(dt.getTime())) return String(valor);
        const d  = String(dt.getDate()).padStart(2, '0');
        const m  = String(dt.getMonth() + 1).padStart(2, '0');
        const y  = dt.getFullYear();
        const h  = String(dt.getHours()).padStart(2, '0');
        const mi = String(dt.getMinutes()).padStart(2, '0');
        return `${d}/${m}/${y} ${h}:${mi}`;
    } catch (e) {
        return String(valor);
    }
}

// ================================================================
// DOWNLOAD CSV — PAGAMENTOS DO OPERADOR
// ================================================================

/**
 * Exporta para CSV os pagamentos visíveis na aba de pagamentos do operador.
 * Respeita os filtros ativos (busca, fase, data início/fim).
 */
function exportarPagamentosCSVOperador() {
    // Usa os dados em memória filtrados
    const dados = (window._pagamentosOperadorFiltrados || window._pagamentosOperadorData || []);

    if (!dados.length) {
        alert('Nenhum dado para exportar.');
        return;
    }

    const cabecalho = ['Data Pgto', 'Cliente', 'Contrato', 'Valor', 'Fase Atraso'];
    const linhas = dados.map(p => [
        p.dtPgto || '',
        `"${(p.cliente || '').replace(/"/g, '""')}"`,
        p.contrato || '',
        String(p.valorTotal || '').replace('.', ','),
        p.faseAtraso || ''
    ]);

    const csvContent = [cabecalho.join(';'), ...linhas.map(l => l.join(';'))].join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `pagamentos_operador_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

window.exportarPagamentosCSVOperador = exportarPagamentosCSVOperador;
window._formatarDataAcionamento      = _formatarDataAcionamento;

// ================================================================
// MULTISELECT DE FAIXAS DE ATRASO — OPERADOR
// ================================================================

function toggleDropdownMultiselectOp() {
    const content = document.getElementById('dropdown-faixas-content-op');
    if (content) {
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    }
}

function toggleTodasFaixasOp(chkTodos) {
    const checkboxes = document.querySelectorAll('.chk-faixa-item-op');
    checkboxes.forEach(chk => {
        chk.checked = false; // desmarca individuais se marcou "Todas"
    });
    atualizarSelecaoFaixasOp();
}

function atualizarSelecaoFaixasOp() {
    const chkTodos = document.getElementById('chk-faixa-todas-op');
    const chkItems = document.querySelectorAll('.chk-faixa-item-op');
    const inputHidden = document.getElementById('filtro-faixa-op');
    const labelSelected = document.getElementById('label-faixas-selecionadas-op');

    const selecionadas = [];
    chkItems.forEach(chk => {
        if (chk.checked) selecionadas.push(chk.value);
    });

    if (selecionadas.length > 0) {
        if (chkTodos) chkTodos.checked = false;
        const valorFiltro = selecionadas.join(',');
        if (inputHidden) inputHidden.value = valorFiltro;
        if (labelSelected) {
            if (selecionadas.length <= 2) {
                labelSelected.textContent = selecionadas.join(', ');
            } else {
                labelSelected.textContent = `${selecionadas.length} selecionadas`;
            }
        }
    } else {
        if (chkTodos) chkTodos.checked = true;
        if (inputHidden) inputHidden.value = 'todas';
        if (labelSelected) labelSelected.textContent = 'Todas as faixas';
    }

    // Chama a filtragem local dos dados
    filtrarDadosPorFaixaOpLocal();
}

/**
 * Filtra localmente no frontend os dados que vieram da API de resumo do operador
 * de acordo com a seleção de faixas de atraso, recalculando faturamento, metas,
 * projeções e feito/dia instantaneamente, sem requisições adicionais de rede.
 */
function filtrarDadosPorFaixaOpLocal() {
    const dados = window.dadosCompletos;
    if (!dados) return;

    const faixaVal = document.getElementById('filtro-faixa-op')?.value || 'todas';
    const tbodyFull = document.getElementById('tabela-pagamentos-full');
    
    // Se selecionou todas as faixas, restaura o estado original da API
    if (faixaVal === 'todas') {
        renderizarDashboard(dados);
        if (dados.ultimos_pagamentos) {
            window._pagamentosOperadorFiltrados = dados.ultimos_pagamentos;
            renderizarPagamentosCompletos(dados.ultimos_pagamentos);
        }
        return;
    }

    const listaFaixas = faixaVal.split(',').map(f => f.trim());
    const pagamentosFiltrados = (dados.ultimos_pagamentos || []).filter(p => {
        const fase = p.faseAtraso || p.fase || '';
        return listaFaixas.includes(fase);
    });

    // Salva a lista filtrada no escopo global para exportação de CSV
    window._pagamentosOperadorFiltrados = pagamentosFiltrados;

    // Recalcula Indicadores Básicos
    const faturamento = pagamentosFiltrados.reduce((sum, p) => sum + parseFloat(p.valorTotal || 0), 0);
    const quantidade = pagamentosFiltrados.length;
    const ticket = quantidade > 0 ? faturamento / quantidade : 0;

    // Recalcula Performance e Meta
    const performance = dados.performance || {};
    const meta = performance.meta || 0;
    const atingido = meta > 0 ? (faturamento / meta) * 100 : 0;

    // Obtém o dia divisor a partir da data de última baixa
    let diaDivisor = new Date().getDate(); // fallback
    if (performance.ultima_baixa_banco) {
        const partesData = performance.ultima_baixa_banco.split('/');
        if (partesData.length === 3) {
            diaDivisor = parseInt(partesData[0]);
        }
    }

    // Calcula o total de dias no mês selecionado
    const filtroAno = parseInt(document.getElementById('filtro-ano')?.value || new Date().getFullYear());
    const filtroMes = parseInt(document.getElementById('filtro-mes')?.value || (new Date().getMonth() + 1));
    const totalDiasCorridosMes = new Date(filtroAno, filtroMes, 0).getDate();

    const feitoDiario = diaDivisor > 0 ? faturamento / diaDivisor : 0;
    const projecao = feitoDiario * totalDiasCorridosMes;
    const projecaoPercentual = meta > 0 ? (projecao / meta) * 100 : 0;

    const falta_70 = Math.max(0, (meta * 0.7) - faturamento);
    const falta_80 = Math.max(0, (meta * 0.8) - faturamento);
    const falta_90 = Math.max(0, (meta * 0.9) - faturamento);
    const falta_100 = Math.max(0, meta - faturamento);

    // Clona o objeto de dados original
    const dadosFiltrados = JSON.parse(JSON.stringify(dados));
    
    // Injeta os indicadores recalculados
    dadosFiltrados.indicadores.faturamento_total = faturamento;
    dadosFiltrados.indicadores.total_pagamentos = quantidade;
    dadosFiltrados.indicadores.ticket_medio = ticket;

    dadosFiltrados.performance.faturamento = faturamento;
    dadosFiltrados.performance.quantidade = quantidade;
    dadosFiltrados.performance.feito_diario = feitoDiario;
    dadosFiltrados.performance.atingido_meta = atingido;
    dadosFiltrados.performance.projecao = projecao;
    dadosFiltrados.performance.projecao_percentual = projecaoPercentual;
    dadosFiltrados.performance.falta_70 = falta_70;
    dadosFiltrados.performance.falta_80 = falta_80;
    dadosFiltrados.performance.falta_90 = falta_90;
    dadosFiltrados.performance.falta_100 = falta_100;

    dadosFiltrados.ultimos_pagamentos = pagamentosFiltrados;

    // Renderiza o painel principal com os dados recalculados!
    renderizarDashboard(dadosFiltrados);
    
    // Atualiza a tabela completa na aba de pagamentos
    renderizarPagamentosCompletos(pagamentosFiltrados);
}

// Event listener global para fechar o dropdown ao clicar fora do componente de faixas do operador
document.addEventListener('click', function(event) {
    const container = document.getElementById('multiselect-faixa-op-container');
    const content = document.getElementById('dropdown-faixas-content-op');
    if (container && content && !container.contains(event.target)) {
        content.style.display = 'none';
    }
});

// Expõe globalmente
window.toggleDropdownMultiselectOp = toggleDropdownMultiselectOp;
window.toggleTodasFaixasOp          = toggleTodasFaixasOp;
window.atualizarSelecaoFaixasOp     = atualizarSelecaoFaixasOp;
window.filtrarDadosPorFaixaOpLocal  = filtrarDadosPorFaixaOpLocal;

// ================================================================
// HORÁRIOS / PONTO ELETRÔNICO (OPERADOR)
// ================================================================

// Array em memória para guardar os pontos do mês
let _pontosMockados = [];
let _relogioIntervalId = null;

/**
 * Inicializa o relógio dinâmico no card de Ponto Eletrônico.
 * Atualiza o horário a cada segundo e formata a data atual.
 */
function inicializarRelogioPonto() {
    const relogio = document.getElementById('ponto-relogio');
    const dataEl = document.getElementById('ponto-data');
    if (!relogio || !dataEl) return;

    // Cancela interval anterior se existir
    if (_relogioIntervalId) {
        clearInterval(_relogioIntervalId);
    }

    function atualizarTempo() {
        const agora = new Date();
        const hrs = String(agora.getHours()).padStart(2, '0');
        const mins = String(agora.getMinutes()).padStart(2, '0');
        const secs = String(agora.getSeconds()).padStart(2, '0');
        relogio.textContent = `${hrs}:${mins}:${secs}`;
    }

    // Configura data atual por extenso
    const opcoes = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dataEl.textContent = new Date().toLocaleDateString('pt-BR', opcoes);

    atualizarTempo();
    _relogioIntervalId = setInterval(atualizarTempo, 1000);
}

/**
 * Gera e renderiza a tabela de espelho de ponto eletrônico para o operador.
 * Utiliza o turno dele (obtido da sessão) para gerar entradas/saídas realistas.
 */
async function renderizarPontoOperador() {
    const login = window.operadorLogado?.login;
    if (!login) return;

    try {
        const response = await fetch(`/api/horarios/${login}`);
        const result = await response.json();

        if (!result.success || !result.data) {
            console.error('Erro ao carregar horarios do operador:', result.message);
            return;
        }

        const data = result.data;
        const ponto = data.ponto || {};
        const cardD1 = ponto.card_d1 || {};
        const historico = ponto.historico_mes || [];

        // Preenche o perfil no topo — foto + nome + metadados
        const elFoto = document.getElementById('ponto-op-foto');
        const elFotoFallback = document.getElementById('ponto-op-foto-fallback');
        if (elFoto) {
            if (data.imagem) {
                elFoto.src = data.imagem;
                elFoto.style.display = 'block';
                if (elFotoFallback) elFotoFallback.style.display = 'none';
            } else {
                elFoto.style.display = 'none';
                if (elFotoFallback) elFotoFallback.style.display = 'flex';
            }
        }

        const elNome = document.getElementById('ponto-op-nome');
        const elTempoCasa = document.getElementById('ponto-op-tempo-casa');
        const elBanco = document.getElementById('ponto-op-banco');
        const elDataRef = document.getElementById('ponto-op-data-ref');
        const elAtualizacao = document.getElementById('ponto-op-ultima-atualizacao');

        if (elNome) elNome.textContent = data.nome || login;
        if (elTempoCasa) elTempoCasa.textContent = data.tempo_casa || '—';
        if (elBanco) elBanco.textContent = data.banco || '—';
        if (elDataRef) elDataRef.textContent = cardD1.data || '—';
        if (elAtualizacao) {
            const raw = data.ultima_atualizacao || '';
            if (raw) {
                try {
                    const dt = new Date(raw.replace(' ', 'T'));
                    elAtualizacao.textContent = dt.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
                } catch(e) { elAtualizacao.textContent = raw; }
            } else {
                elAtualizacao.textContent = 'Hoje';
            }
        }

        // Preenche os cards
        const elBancoHoras = document.getElementById('card-ponto-banco-horas');
        const elEnt1 = document.getElementById('card-ponto-ent1');
        const elSai1 = document.getElementById('card-ponto-sai1');
        const elEnt2 = document.getElementById('card-ponto-ent2');
        const elSai2 = document.getElementById('card-ponto-sai2');

        if (elBancoHoras) {
            const saldo = cardD1.b_saldo || '00:00';
            const ehNegativo = saldo.startsWith('-');
            const corSaldo = ehNegativo ? '#ef4444' : '#10b981';

            elBancoHoras.textContent = saldo;
            elBancoHoras.style.color = corSaldo;

            // Atualiza o saldo do Banco de Horas no cabeçalho do perfil (topo direito)
            const elHeaderSaldo = document.getElementById('headerBancoHorasSaldo');
            if (elHeaderSaldo) {
                elHeaderSaldo.innerHTML = `Banco de Horas: <span style="color:${corSaldo};font-weight:800;">${saldo}</span>`;
            }
        }
        if (elEnt1) elEnt1.textContent = cardD1.entrada1 || '—';
        if (elSai1) elSai1.textContent = cardD1.saida1 || '—';
        if (elEnt2) elEnt2.textContent = cardD1.entrada2 || '—';
        if (elSai2) elSai2.textContent = cardD1.saida2 || '—';

        // Renderiza a tabela de histórico
        const tbody = document.getElementById('tabela-ponto-operador');
        if (!tbody) return;

        if (historico.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted);">Nenhum lançamento encontrado para o mês atual.</td></tr>`;
            return;
        }

        tbody.innerHTML = historico.map((p, idx) => {
            const bSaldoStr = p.b_saldo || '';
            const saldoCor = bSaldoStr.startsWith('+') ? '#10b981' : (bSaldoStr.startsWith('-') ? '#ef4444' : 'var(--text-main)');
            const bgRow = idx % 2 === 0 ? '#ffffff' : '#f9fafb';
            return `
                <tr style="background:${bgRow}; transition: all 0.2s;">
                    <td style="text-align:center;font-weight:600;padding:10px 14px;">${p.data || '—'}</td>
                    <td style="text-align:center;padding:10px 14px;font-family:monospace;">${p.entrada1 || '—'}</td>
                    <td style="text-align:center;padding:10px 14px;font-family:monospace;">${p.saida1 || '—'}</td>
                    <td style="text-align:center;padding:10px 14px;font-family:monospace;">${p.entrada2 || '—'}</td>
                    <td style="text-align:center;padding:10px 14px;font-family:monospace;">${p.saida2 || '—'}</td>
                    <td style="text-align:center;font-weight:700;color:${saldoCor};padding:10px 14px;">${p.b_saldo || '—'}</td>
                    <td style="text-align:center;font-weight:700;padding:10px 14px;">${p.b_total || '—'}</td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        console.error('Erro ao renderizar ponto do operador:', err);
    }
}


/**
 * Gera os pontos diários do mês até a data de hoje de forma realista.
 */
function _gerarPontosMêsAtual(turno) {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = hoje.getMonth();
    const diaAtual = hoje.getDate();

    // Determina o horário padrão baseado no turno
    let padraoEnt1 = "08:00", padraoSai1 = "12:00", padraoEnt2 = "13:00", padraoSai2 = "17:00";
    if (turno.includes("13:") || turno.includes("Tarde")) {
        padraoEnt1 = "13:00"; padraoSai1 = "17:00"; padraoEnt2 = "18:00"; padraoSai2 = "22:00";
    }

    _pontosMockados = [];

    // Preenche do dia 1 até hoje
    for (let d = 1; d <= diaAtual; d++) {
        const dataDia = new Date(ano, mes, d);
        
        // Ignora fins de semana para o espelho
        if (dataDia.getDay() === 0 || dataDia.getDay() === 6) {
            continue;
        }

        const dataFmt = String(d).padStart(2, '0') + '/' + String(mes + 1).padStart(2, '0') + '/' + ano;

        // Se for o dia de hoje, gera entradas parciais dependendo da hora atual
        if (d === diaAtual) {
            const horaAgora = hoje.getHours();
            let ent1 = '', sai1 = '', ent2 = '', sai2 = '', total = '—', saldo = '—';
            
            if (horaAgora >= 8) ent1 = padraoEnt1;
            if (horaAgora >= 12) sai1 = padraoSai1;
            if (horaAgora >= 13) ent2 = padraoEnt2;
            if (horaAgora >= 17) {
                sai2 = padraoSai2;
                total = "08h 00min";
                saldo = "0h 00min";
            }

            _pontosMockados.push({
                data: dataFmt,
                ent1, sai1, ent2, sai2, total, saldo
            });
            continue;
        }

        // Para dias passados, gera uma pequena variação para dar realismo
        let ent1 = padraoEnt1, sai1 = padraoSai1, ent2 = padraoEnt2, sai2 = padraoSai2;
        let total = "08h 00min", saldo = "0h 00min";

        // Cria variações em alguns dias (atrasos ou extras)
        if (d % 7 === 0) {
            // Dia com 15 min de hora extra
            const m = parseInt(padraoSai2.split(':')[1]) + 15;
            sai2 = padraoSai2.split(':')[0] + ':' + String(m).padStart(2, '0');
            total = "08h 15min";
            saldo = "+15min";
        } else if (d % 11 === 0) {
            // Dia com atraso de 15 min na entrada 1
            const m = parseInt(padraoEnt1.split(':')[1]) + 15;
            ent1 = padraoEnt1.split(':')[0] + ':' + String(m).padStart(2, '0');
            total = "07h 45min";
            saldo = "-15min";
        }

        _pontosMockados.push({
            data: dataFmt,
            ent1, sai1, ent2, sai2, total, saldo
        });
    }

    // Ordena do mais recente para o mais antigo na tabela
    _pontosMockados.reverse();
}

/**
 * Simula a batida de ponto eletrônico do operador na hora atual.
 * Atualiza o registro do dia de hoje na tabela com animação.
 */
function simularBaterPonto() {
    const agora = new Date();
    const hrs = String(agora.getHours()).padStart(2, '0');
    const mins = String(agora.getMinutes()).padStart(2, '0');
    const horaFmt = `${hrs}:${mins}`;

    // Procura o registro do dia de hoje no array (primeiro elemento por causa da reversão)
    const hojeFmt = String(agora.getDate()).padStart(2, '0') + '/' + String(agora.getMonth() + 1).padStart(2, '0') + '/' + agora.getFullYear();
    const pontoHoje = _pontosMockados.find(p => p.data === hojeFmt);

    if (pontoHoje) {
        let batidaTipo = '';
        
        if (!pontoHoje.ent1) {
            pontoHoje.ent1 = horaFmt;
            batidaTipo = 'Entrada 1';
        } else if (!pontoHoje.sai1) {
            pontoHoje.sai1 = horaFmt;
            batidaTipo = 'Saída 1 (Intervalo)';
        } else if (!pontoHoje.ent2) {
            pontoHoje.ent2 = horaFmt;
            batidaTipo = 'Entrada 2 (Retorno)';
        } else if (!pontoHoje.sai2) {
            pontoHoje.sai2 = horaFmt;
            pontoHoje.total = "08h 00min";
            pontoHoje.saldo = "0h 00min";
            batidaTipo = 'Saída 2 (Fim do Expediente)';
        } else {
            alert('Todos os 4 registros do ponto de hoje já foram preenchidos!');
            return;
        }

        // Toca animação no botão
        const btn = document.getElementById('btn-bater-ponto');
        if (btn) {
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => { btn.style.transform = 'scale(1)'; }, 150);
        }

        // Recarrega a tabela
        renderizarPontoOperador();

        // Notifica o operador
        alert(`Sucesso! Batida de [${batidaTipo}] registrada às ${horaFmt}.`);
    } else {
        alert('Não foi possível localizar o registro para o dia de hoje.');
    }
}

// Expõe para uso nos escopos onclick
window.inicializarRelogioPonto = inicializarRelogioPonto;
window.renderizarPontoOperador = renderizarPontoOperador;
window.simularBaterPonto        = simularBaterPonto;

// ================================================================
// VISÃO TRIMESTRAL POR DIA ÚTIL — OPERADOR
// ================================================================
// Renderiza a tabela comparativa de 3 meses com recebimento por
// dia útil (somente seg a sex), facilitando análise dia-a-dia.

function renderizarTrimestreDUOp(trimestre) {
    const tbody = document.getElementById('tabela-trimestre-du-op');
    if (!tbody) return;

    // Backend retorna: { colunas: [m0, m1, m2], linhas: [{dia_util, data_atual, v_atual, v_m1, v_m2}], totais: {...} }
    if (!trimestre || !trimestre.linhas || trimestre.linhas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#6B7280;padding:20px;">Dados trimestrais n\u00e3o dispon\u00edveis.</td></tr>';
        return;
    }

    // Atualiza cabe\u00e7alhos com o nome dos meses
    const thM0 = document.getElementById('th-trimestre-m0');
    const thM1 = document.getElementById('th-trimestre-m1');
    const thM2 = document.getElementById('th-trimestre-m2');
    if (thM0 && trimestre.colunas?.[0]) thM0.textContent = trimestre.colunas[0];
    if (thM1 && trimestre.colunas?.[1]) thM1.textContent = trimestre.colunas[1];
    if (thM2 && trimestre.colunas?.[2]) thM2.textContent = trimestre.colunas[2];

    let html = trimestre.linhas.map(linha => {
        // Backend usa: dia_util, data_atual, v_atual, v_m1, v_m2
        const v0 = linha.v_atual || 0;
        const v1 = linha.v_m1 || 0;
        const v2 = linha.v_m2 || 0;
        const corM0 = v0 >= v1 ? '#16a34a' : '#dc2626';

        return `
            <tr>
                <td style="text-align:center;font-weight:700;color:var(--purple-main);">${linha.dia_util || '—'}</td>
                <td style="text-align:center;">${linha.data_atual || '—'}</td>
                <td style="text-align:center;font-weight:700;color:${corM0};">${formatarMoeda(v0)}</td>
                <td style="text-align:center;color:#6b7280;">${formatarMoeda(v1)}</td>
                <td style="text-align:center;color:#9ca3af;">${formatarMoeda(v2)}</td>
            </tr>
        `;
    }).join('');

    // Linha de totais vinda do backend
    const t = trimestre.totais || {};
    html += `
        <tr style="background:#ede9fe;font-weight:800;">
            <td colspan="2" style="text-align:center;color:#4a1d8c;padding:10px;">TOTAL DO PERÍODO</td>
            <td style="text-align:center;color:#4a1d8c;">${formatarMoeda(t.total_atual || 0)}</td>
            <td style="text-align:center;color:#4a1d8c;">${formatarMoeda(t.total_m1 || 0)}</td>
            <td style="text-align:center;color:#4a1d8c;">${formatarMoeda(t.total_m2 || 0)}</td>
        </tr>
    `;

    tbody.innerHTML = html;
}
window.renderizarTrimestreDUOp = renderizarTrimestreDUOp;

// ================================================================
// RELATÓRIO FAIXA DE ATRASO VS MÊS — OPERADOR (EXCLUSIVO SEMEAR)
// ================================================================
// Renderiza a matriz de Faixas de Atraso x 12 Meses do Ano.
// Exibido apenas quando o banco do operador for SEMEAR.

function renderizarMatrizFaixasOp(matriz) {
    const container = document.getElementById('card-faixas-vs-mes-op-container');
    const tbody = document.getElementById('tabela-faixa-vs-mes-op');
    if (!tbody || !container) return;

    if (!matriz || !matriz.linhas || matriz.linhas.length === 0) {
        container.style.display = 'none';
        return;
    }

    // Exibe o card apenas para SEMEAR
    container.style.display = 'block';

    const mesesAbrev = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];

    let html = '';
    let totalGeralPorMes = new Array(12).fill(0);

    // Encontra os valores máximos por coluna para highlight
    const maxPorMes = new Array(12).fill(0);
    matriz.linhas.forEach(linha => {
        if (linha.faixa === 'TOTAL GERAL') return;
        mesesAbrev.forEach((mes, idx) => {
            const v = linha[mes] || 0;
            if (v > maxPorMes[idx]) maxPorMes[idx] = v;
        });
    });

    matriz.linhas.forEach(linha => {
        if (linha.faixa === 'TOTAL GERAL') return;
        let celulas = '';
        mesesAbrev.forEach((mes, idx) => {
            const v = linha[mes] || 0;
            totalGeralPorMes[idx] += v;
            const destaque = (v > 0 && v === maxPorMes[idx]) ? 'background:#f3e8ff;font-weight:800;color:#6d28d9;' : '';
            celulas += `<td style="text-align:center;padding:8px 10px;${destaque}">${v > 0 ? formatarMoeda(v) : '—'}</td>`;
        });
        html += `
            <tr>
                <td style="padding:8px 12px;font-weight:700;white-space:nowrap;border-right:2px solid #e5e7eb;color:var(--purple-main);">${linha.faixa}</td>
                ${celulas}
                <td style="text-align:center;padding:8px 10px;font-weight:800;background:#f3e8ff;color:#5b21b6;">${formatarMoeda(linha.total_ano || 0)}</td>
            </tr>
        `;
    });

    // Linha de totais por mês
    const t = matriz.totais || {};
    const celulasTotais = mesesAbrev.map(mes =>
        `<td style="text-align:center;padding:8px 10px;font-weight:800;color:#5b21b6;">${formatarMoeda(t[mes] || 0)}</td>`
    ).join('');
    html += `
        <tr style="background:#f3e8ff;">
            <td style="padding:8px 12px;font-weight:800;color:#4a1d8c;border-right:2px solid #e5e7eb;">TOTAL</td>
            ${celulasTotais}
            <td style="text-align:center;font-weight:800;padding:8px 10px;background:#ede9fe;color:#4a1d8c;">${formatarMoeda(t.total_ano || 0)}</td>
        </tr>
    `;

    tbody.innerHTML = html;
}
window.renderizarMatrizFaixasOp = renderizarMatrizFaixasOp;

// ================================================================
// FILTRAR PELA DATA ATUAL DO DU (BOTÃO "ATÉ DU ATUAL")
// ================================================================

// Preenche os campos de dia útil com 1 e o DU atual do mês,
// e recarrega todos os dados da página automaticamente.

function filtrarDUAtual() {
    const duFimEl = document.getElementById('filtro-du-fim');
    const duInicioEl = document.getElementById('filtro-du-inicio');
    if (!duFimEl || !duInicioEl) return;

    // Calcula quantos dias úteis já passaram no mês atual
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = hoje.getMonth(); // 0-indexed
    let duContador = 0;

    for (let d = 1; d <= hoje.getDate(); d++) {
        const dia = new Date(ano, mes, d);
        const dow = dia.getDay(); // 0=dom, 6=sab
        if (dow >= 1 && dow <= 5) duContador++;
    }

    duInicioEl.value = 1;
    duFimEl.value = Math.max(1, duContador);

    // Recarrega com o novo filtro de DU
    if (typeof carregarDados === 'function') carregarDados();
}
window.filtrarDUAtual = filtrarDUAtual;