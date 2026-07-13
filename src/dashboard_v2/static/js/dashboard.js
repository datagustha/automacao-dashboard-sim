/**
 * DASHBOARD - Funções Específicas
 * ================================
 */

// ================================================================
// RENDERIZAÇÃO - DASHBOARD
// ================================================================

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
    const ticketAntEl = document.getElementById('kpi-ticket-anterior');
    if (ticketAntEl) {
        ticketAntEl.textContent = `← Mês anterior: ${formatarMoeda(ticketAnt)}`;
    }
    
    // Total de Pagamentos
    const totalPgtos = indicadores.total_pagamentos || 0;
    const totalPgtosAnt = indicadoresAnt.total_pagamentos || 0;
    document.getElementById('kpi-total-pgtos').textContent = totalPgtos;
    const totalPgtosAntEl = document.getElementById('kpi-total-pgtos-anterior');
    if (totalPgtosAntEl) {
        totalPgtosAntEl.textContent = `← Mês anterior: ${totalPgtosAnt}`;
    }
    
    // Meta
    const meta = performance.meta || 0;
    const atingido = performance.atingido_meta || 0;
    document.getElementById('kpi-meta-objetivo').textContent = formatarMoeda(meta);
    document.getElementById('kpi-meta-barra').style.width = Math.min(atingido, 100) + '%';
    document.getElementById('kpi-meta-percentual').textContent = atingido.toFixed(1) + '%';
    
    // Rodapé de Meta — duas colunas: Mês Anterior | Diferença da Meta (ADM style)
    const variacaoFat = faturamentoAnt > 0 ? ((faturamento - faturamentoAnt) / faturamentoAnt) * 100 : 0;
    const faltaFat = Math.max(0, meta - faturamento);
    const faltaFatPct = meta > 0 ? (faltaFat / meta) * 100 : 0;
    
    const corVar = variacaoFat >= 0 ? '#16a34a' : '#dc2626';
    const bgVar = variacaoFat >= 0 ? '#dcfce7' : '#fee2e2';
    const seta = variacaoFat >= 0 ? '▲' : '▼';
    const faltaHtml = faltaFat > 0
        ? `<span style="font-weight:700;color:var(--text-main);font-size:12px;">Falta: ${formatarMoeda(faltaFat)}</span>
           <span style="color:#d97706;background:#fef3c7;padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:4px;">${faltaFatPct.toFixed(1)}% abaixo</span>`
        : `<span style="font-weight:700;color:#16a34a;font-size:12px;">Meta Atingida! 🎉</span>`;
        
    const footerMetaEl = document.getElementById('kpi-meta-anterior-detalhe');
    if (footerMetaEl) {
        footerMetaEl.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
                <div>
                    <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                    <div style="display:flex;align-items:center;">
                        <span style="font-weight:700;color:var(--text-main);font-size:12px;">${formatarMoeda(faturamentoAnt)}</span>
                        <span style="color:${corVar};background:${bgVar};padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:6px;">${seta} ${Math.abs(variacaoFat).toFixed(1)}%</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença da Meta</span>
                    <div style="display:flex;align-items:center;justify-content:flex-end;">${faltaHtml}</div>
                </div>
            </div>
        `;
    }
    
    // ============================================================
    // TMA (Métricas de Ligação)
    // ============================================================
    if (dados.tma) {
        document.getElementById('kpi-tma-valor').textContent = dados.tma.tma || '—';
        document.getElementById('kpi-tma-acionamentos').textContent = dados.tma.acionamentos || 0;
        document.getElementById('kpi-tma-reacionamento').textContent = (dados.tma.taxa || '0,0') + '%';
    }
    
    // ============================================================
    // GRÁFICOS
    // ============================================================
    const graficoEvolucao = document.getElementById('grafico-evolucao');
    if (graficoEvolucao) {
        graficoEvolucao.innerHTML = criarGraficoEvolucao(dados.faturamento_dia || []);
    }
    
    const graficoFase = document.getElementById('grafico-fase');
    if (graficoFase) {
        graficoFase.innerHTML = criarGraficoFase(dados.pagamentos_fase || []);
    }
    
    // ============================================================
    // PERFORMANCE
    // ============================================================
    renderizarPerformance(performance);
    
    // ============================================================
    // PAGAMENTOS
    // ============================================================
    renderizarPagamentos(dados.ultimos_pagamentos || []);
    
    // ============================================================
    // METAS
    // ============================================================
    renderizarMetas(dados.metas || []);
    
    // ============================================================
    // EVOLUÇÃO
    // ============================================================
    renderizarEvolucao(dados);
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
            <td><strong>${p.contrato || '-'}</strong></td>
            <td>${p.cliente || '-'}</td>
            <td>${formatarMoeda(p.valorTotal || 0)}</td>
            <td>${formatarData(p.dtPgto)}</td>
            <td>${renderizarStatus(p.faseAtraso)}</td>
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
        
        return `
            <tr>
                <td>${mesAno}</td>
                <td>${formatarMoeda(m.meta70 || 0)}</td>
                <td>${formatarMoeda(m.meta80 || 0)}</td>
                <td>${formatarMoeda(m.meta90 || 0)}</td>
                <td><strong>${formatarMoeda(m.meta100 || 0)}</strong></td>
                <td>${m.atingido ? formatarMoeda(m.atingido) : '—'}</td>
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

function aplicarFiltroPagamentos() {
    const tbody = document.getElementById('tabela-pagamentos-full');
    const totalRegistros = document.getElementById('total-registros');
    if (!tbody || !totalRegistros) return;
    
    const busca = document.getElementById('filtro-pagamento-busca');
    const fase = document.getElementById('filtro-pagamento-fase');
    
    const buscaText = busca ? busca.value.toLowerCase() : '';
    const faseText = fase ? fase.value : '';
    
    let filtrados = pagamentosCompletos;
    
    if (buscaText) {
        filtrados = filtrados.filter(p => 
            (p.cliente || '').toLowerCase().includes(buscaText) ||
            (p.contrato || '').toLowerCase().includes(buscaText)
        );
    }
    
    if (faseText) {
        filtrados = filtrados.filter(p => (p.faseAtraso || '') === faseText);
    }
    
    if (filtrados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#6B7280;padding:30px;">Nenhum pagamento encontrado</td></tr>';
    } else {
        const totalFaturamento = filtrados.reduce((sum, p) => sum + (p.valorTotal || 0), 0);
        
        tbody.innerHTML = filtrados.map(p => `
            <tr>
                <td><strong>${p.contrato || '-'}</strong></td>
                <td>${p.cliente || '-'}</td>
                <td>${p.produto || p.fase || '-'}</td>
                <td>${formatarMoeda(p.valorTotal || 0)}</td>
                <td>${formatarData(p.dtPgto)}</td>
                <td>${p.faseAtraso || '-'}</td>
                <td>${renderizarStatus(p.faseAtraso)}</td>
            </tr>
        `).join('') + `
            <tr class="sticky-total-row">
                <td><strong>📊 TOTAL</strong></td>
                <td>-</td>
                <td>-</td>
                <td><strong>${formatarMoeda(totalFaturamento)}</strong></td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
            </tr>
        `;
    }
    
    totalRegistros.textContent = `${filtrados.length} registros`;
}

function filtrarPagamentos() {
    aplicarFiltroPagamentos();
}