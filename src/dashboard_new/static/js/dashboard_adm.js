/**
 * DASHBOARD ADM - Funções Específicas
 * ====================================
 */

// ================================================================
// RENDERIZAÇÃO - DASHBOARD ADM
// ================================================================

function renderizarDashboardAdm(dados) {
    if (!dados) {
        console.warn('⚠️ Dados não fornecidos para renderizarDashboardAdm');
        return;
    }

    // ============================================================
    // CARDS - SEMEAR e AGORACRED (com rodapé completo)
    // ============================================================
    const semear = dados.semear || {};
    const agoracred = dados.agoracred || {};

    // --- SEMEAR ---
    const fatSemear = semear.faturamento || 0;
    const metaSemear = semear.meta || 0;
    const percSemear = metaSemear > 0 ? (fatSemear / metaSemear) * 100 : 0;
    const anteriorSemear = semear.anterior || 0;
    const variacaoSemear = anteriorSemear > 0 ? ((fatSemear - anteriorSemear) / anteriorSemear) * 100 : 0;
    const faltaSemear = Math.max(0, metaSemear - fatSemear);
    const faltaSemearPct = metaSemear > 0 ? (faltaSemear / metaSemear) * 100 : 0;

    document.getElementById('kpi-fat-semear').textContent = formatarMoeda(fatSemear);
    document.getElementById('kpi-meta-semear').textContent = formatarMoeda(metaSemear);
    document.getElementById('kpi-percentual-semear').textContent = percSemear.toFixed(1) + '%';
    document.getElementById('barra-progresso-semear').style.width = Math.min(percSemear, 100) + '%';

    // Sub-info Semear: Qtd. Pagamentos e Ticket Médio
    const opsSemearEl = document.getElementById('kpi-ops-semear');
    const ticketSemearEl = document.getElementById('kpi-ticket-semear');
    if (opsSemearEl) opsSemearEl.textContent = semear.operacoes || 0;
    if (ticketSemearEl) ticketSemearEl.textContent = formatarMoeda(semear.ticket_medio || 0);


    // Rodapé SEMEAR — duas colunas: Mês Anterior | Diferença da Meta
    const corVarSemear = variacaoSemear >= 0 ? '#16a34a' : '#dc2626';
    const bgVarSemear = variacaoSemear >= 0 ? '#dcfce7' : '#fee2e2';
    const setaSemear = variacaoSemear >= 0 ? '▲' : '▼';
    const faltaSemearHtml = faltaSemear > 0
        ? `<span style="font-weight:700;color:var(--text-main);font-size:12px;">Falta: ${formatarMoeda(faltaSemear)}</span>
           <span style="color:#d97706;background:#fef3c7;padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:4px;">${faltaSemearPct.toFixed(1)}% abaixo</span>`
        : `<span style="font-weight:700;color:#16a34a;font-size:12px;">Meta Atingida! <i class=\"fas fa-check-circle\"></i></span>`;

    document.getElementById('kpi-fat-semear-anterior').innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
            <div>
                <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                <div style="display:flex;align-items:center;">
                    <span style="font-weight:700;color:var(--text-main);font-size:12px;">${formatarMoeda(anteriorSemear)}</span>
                    <span style="color:${corVarSemear};background:${bgVarSemear};padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:6px;">${setaSemear} ${Math.abs(variacaoSemear).toFixed(1)}%</span>
                </div>
            </div>
            <div style="text-align:right;">
                <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença da Meta</span>
                <div style="display:flex;align-items:center;justify-content:flex-end;">${faltaSemearHtml}</div>
            </div>
        </div>
    `;

    // --- AGORACRED ---
    const fatAgoracred = agoracred.faturamento || 0;
    const metaAgoracred = agoracred.meta || 0;
    const percAgoracred = metaAgoracred > 0 ? (fatAgoracred / metaAgoracred) * 100 : 0;
    const anteriorAgoracred = agoracred.anterior || 0;
    const variacaoAgoracred = anteriorAgoracred > 0 ? ((fatAgoracred - anteriorAgoracred) / anteriorAgoracred) * 100 : 0;
    const faltaAgoracred = Math.max(0, metaAgoracred - fatAgoracred);
    const faltaAgoracredPct = metaAgoracred > 0 ? (faltaAgoracred / metaAgoracred) * 100 : 0;

    document.getElementById('kpi-fat-agoracred').textContent = formatarMoeda(fatAgoracred);
    document.getElementById('kpi-meta-agoracred').textContent = formatarMoeda(metaAgoracred);
    document.getElementById('kpi-percentual-agoracred').textContent = percAgoracred.toFixed(1) + '%';
    document.getElementById('barra-progresso-agoracred').style.width = Math.min(percAgoracred, 100) + '%';

    // Sub-info Agoracred: Qtd. Pagamentos e Ticket Médio
    const opsAgoracredEl = document.getElementById('kpi-ops-agoracred');
    const ticketAgoracredEl = document.getElementById('kpi-ticket-agoracred');
    if (opsAgoracredEl) opsAgoracredEl.textContent = agoracred.operacoes || 0;
    if (ticketAgoracredEl) ticketAgoracredEl.textContent = formatarMoeda(agoracred.ticket_medio || 0);


    // Rodapé AGORACRED — duas colunas
    const corVarAgoracred = variacaoAgoracred >= 0 ? '#16a34a' : '#dc2626';
    const bgVarAgoracred = variacaoAgoracred >= 0 ? '#dcfce7' : '#fee2e2';
    const setaAgoracred = variacaoAgoracred >= 0 ? '▲' : '▼';
    const faltaAgoracredHtml = faltaAgoracred > 0
        ? `<span style="font-weight:700;color:var(--text-main);font-size:12px;">Falta: ${formatarMoeda(faltaAgoracred)}</span>
           <span style="color:#d97706;background:#fef3c7;padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:4px;">${faltaAgoracredPct.toFixed(1)}% abaixo</span>`
        : `<span style="font-weight:700;color:#16a34a;font-size:12px;">Meta Atingida! <i class=\"fas fa-check-circle\"></i></span>`;

    document.getElementById('kpi-fat-agoracred-anterior').innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
            <div>
                <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                <div style="display:flex;align-items:center;">
                    <span style="font-weight:700;color:var(--text-main);font-size:12px;">${formatarMoeda(anteriorAgoracred)}</span>
                    <span style="color:${corVarAgoracred};background:${bgVarAgoracred};padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:6px;">${setaAgoracred} ${Math.abs(variacaoAgoracred).toFixed(1)}%</span>
                </div>
            </div>
            <div style="text-align:right;">
                <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença da Meta</span>
                <div style="display:flex;align-items:center;justify-content:flex-end;">${faltaAgoracredHtml}</div>
            </div>
        </div>
    `;

    // ============================================================
    // CARDS - Linha 2: Operações e Ticket (Storytelling Completo)
    // ============================================================
    const totalOps = dados.total_operacoes || 0;
    const opsAnterior = dados.operacoes_anterior || 0;

    document.getElementById('kpi-total-ops-adm').textContent = totalOps;

    const variacaoOps = opsAnterior > 0 ? ((totalOps - opsAnterior) / opsAnterior) * 100 : 0;
    const difOps = totalOps - opsAnterior;
    const corVarOps = variacaoOps >= 0 ? '#16a34a' : '#dc2626';
    const bgVarOps = variacaoOps >= 0 ? '#dcfce7' : '#fee2e2';
    const setaOps = variacaoOps >= 0 ? '▲' : '▼';
    const sinalOps = difOps >= 0 ? '+' : '';

    const footerOpsEl = document.getElementById('kpi-ops-adm-anterior-detalhe');
    if (footerOpsEl) {
        footerOpsEl.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
                <div>
                    <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                    <div style="display:flex;align-items:center;">
                        <span style="font-weight:700;color:var(--text-main);font-size:12px;">${opsAnterior} pgtos</span>
                        <span style="color:${corVarOps};background:${bgVarOps};padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:6px;">${setaOps} ${Math.abs(variacaoOps).toFixed(1)}%</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença no Período</span>
                    <span style="font-weight:700;color:${corVarOps};font-size:12px;">${sinalOps}${difOps} pgtos</span>
                </div>
            </div>
        `;
    }

    const ticketAtual = dados.ticket_medio || 0;
    const ticketAnterior = dados.ticket_medio_anterior || 0;
    document.getElementById('kpi-ticket-adm').textContent = formatarMoeda(ticketAtual);

    const variacaoTk = ticketAnterior > 0 ? ((ticketAtual - ticketAnterior) / ticketAnterior) * 100 : 0;
    const difTk = ticketAtual - ticketAnterior;
    const corVarTk = variacaoTk >= 0 ? '#16a34a' : '#dc2626';
    const bgVarTk = variacaoTk >= 0 ? '#dcfce7' : '#fee2e2';
    const setaTk = variacaoTk >= 0 ? '▲' : '▼';
    const sinalTk = difTk >= 0 ? '+' : '';

    const footerTkEl = document.getElementById('kpi-ticket-adm-anterior-detalhe');
    if (footerTkEl) {
        footerTkEl.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%;margin-top:4px;">
                <div>
                    <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Mês Anterior</span>
                    <div style="display:flex;align-items:center;">
                        <span style="font-weight:700;color:var(--text-main);font-size:12px;">${formatarMoeda(ticketAnterior)}</span>
                        <span style="color:${corVarTk};background:${bgVarTk};padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:6px;">${setaTk} ${Math.abs(variacaoTk).toFixed(1)}%</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:2px;">Diferença no Período</span>
                    <span style="font-weight:700;color:${corVarTk};font-size:12px;">${sinalTk}${formatarMoeda(difTk)}</span>
                </div>
            </div>
        `;
    }

    // ============================================================
    // GRÁFICOS
    // ============================================================
    const graficoSemear = document.getElementById('grafico-evolucao-semear-adm');
    if (graficoSemear) {
        graficoSemear.innerHTML = criarGraficoEvolucao(semear.evolucao || [], '#7e3d97');
    }

    const graficoAgoracred = document.getElementById('grafico-evolucao-agoracred-adm');
    if (graficoAgoracred) {
        graficoAgoracred.innerHTML = criarGraficoEvolucao(agoracred.evolucao || [], '#10B981');
    }

    // ============================================================
    // TABELA - Evolução Diária
    // ============================================================
    renderizarEvolucaoDiaria(semear.evolucao || [], agoracred.evolucao || []);

    // ============================================================
    // TABELA - Ranking SEMEAR (COM FOTOS)
    // ============================================================
    renderizarRankingSemear(semear.operadores || []);

    // ============================================================
    // TABELA - Ranking AGORACRED (COM FOTOS)
    // ============================================================
    renderizarRankingAgoracred(agoracred.operadores || []);

    // ============================================================
    // TABELA - Faixas SEMEAR (COM FOTOS)
    // ============================================================
    renderizarFaixasSemear(semear.faixas || []);

    // ============================================================
    // TABELA - Evolução Operadores
    // ============================================================
    renderizarEvolucaoOperadores(dados.evolucao_operadores || []);
}

// ================================================================
// AVATAR HELPER
// ================================================================

function _avatarCell(imagem, login, cor) {
    if (imagem) {
        return `<img src="${imagem}" alt="${login}" style="width:34px;height:34px;border-radius:50%;object-fit:cover;border:2px solid ${cor};">`;
    }
    const iniciais = (login || '').replace(/[0-9]/g, '').substring(0, 2).toUpperCase() || 'OP';
    return `<div style="width:34px;height:34px;border-radius:50%;background:${cor};color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;margin:0 auto;">${iniciais}</div>`;
}

// ================================================================
// RENDERIZAÇÃO - EVOLUÇÃO DIÁRIA
// ================================================================

function renderizarEvolucaoDiaria(semear, agoracred) {
    const tbody = document.getElementById('tabela-evolucao-diaria-adm');
    if (!tbody) return;

    // Combina os dados
    const dias = new Set();
    semear.forEach(d => dias.add(d.data));
    agoracred.forEach(d => dias.add(d.data));

    const diasArray = Array.from(dias).sort();

    if (diasArray.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
        return;
    }

    let html = '';
    let totalSemear = 0;
    let totalAgoracred = 0;

    diasArray.forEach(dia => {
        const s = semear.find(d => d.data === dia) || { total: 0 };
        const a = agoracred.find(d => d.data === dia) || { total: 0 };
        const total = (s.total || 0) + (a.total || 0);

        totalSemear += s.total || 0;
        totalAgoracred += a.total || 0;

        // Mostra apenas o dia do mês (1, 2, 3...) como no dashboard antigo
        const diaNumero = dia ? parseInt(dia.split('-')[2], 10) : '-';

        html += `
            <tr>
                <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;font-weight:600;">${diaNumero}</td>
                <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;">${formatarMoeda(s.total || 0)}</td>
                <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;">${formatarMoeda(a.total || 0)}</td>
                <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;font-weight:700;">${formatarMoeda(total)}</td>
            </tr>
        `;
    });

    // Linha de total
    html += `
        <tr style="background:#e9d8fd;font-weight:bold;">
            <td style="padding:10px 14px;text-align:center;color:#4a1d8c;"><strong>TOTAL DO PERÍODO</strong></td>
            <td style="padding:10px 14px;text-align:center;color:#4a1d8c;">${formatarMoeda(totalSemear)}</td>
            <td style="padding:10px 14px;text-align:center;color:#4a1d8c;">${formatarMoeda(totalAgoracred)}</td>
            <td style="padding:10px 14px;text-align:center;color:#4a1d8c;"><strong>${formatarMoeda(totalSemear + totalAgoracred)}</strong></td>
        </tr>
    `;

    tbody.innerHTML = html;
}

// ================================================================
// RENDERIZAÇÃO - RANKING SEMEAR (COM FOTO)
// ================================================================

function renderizarRankingSemear(operadores) {
    const tbody = document.getElementById('tabela-adm-semear');
    if (!tbody) return;

    if (!operadores || operadores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="16" style="text-align:center;color:#6B7280;padding:30px;">Nenhum operador encontrado</td></tr>';
        return;
    }

    // Ordena por faturamento (decrescente)
    operadores.sort((a, b) => (b.faturamento || 0) - (a.faturamento || 0));

    // Pega dias trabalhados e total de dias do mês do primeiro operador (vêm do backend)
    const diasPassados = operadores[0] ? (operadores[0].dias_trabalhados || 1) : 1;
    const totalDiasMes = operadores[0] ? (operadores[0].total_dias_uteis || 1) : 1;

    tbody.innerHTML = operadores.map((op, index) => {
        const percMeta = op.meta > 0 ? ((op.faturamento || 0) / op.meta) * 100 : 0;
        const falta70 = Math.max(0, (op.meta * 0.7) - (op.faturamento || 0));
        const falta80 = Math.max(0, (op.meta * 0.8) - (op.faturamento || 0));
        const falta90 = Math.max(0, (op.meta * 0.9) - (op.faturamento || 0));
        const falta100 = Math.max(0, op.meta - (op.faturamento || 0));
        
        // Calcula falta meta ranking específica
        const metaRankingVal = op.meta_ranking || 0;
        const faltaRanking = Math.max(0, metaRankingVal - (op.faturamento || 0));

        // Projeção: usa o campo do backend se disponível, senão calcula
        const diasOp = op.dias_trabalhados || diasPassados;
        const projecao = op.projecao !== undefined ? op.projecao
            : (diasOp > 0 ? ((op.faturamento || 0) / diasOp) * (op.total_dias_uteis || totalDiasMes) : 0);
        const projecaoPct = op.meta > 0 ? (projecao / op.meta) * 100 : 0;
        const corTextoNeutro = '#374151'; // Preto acinzentado conforme solicitado

        let medalha = '';
        if (index === 0) medalha = '🥇';
        else if (index === 1) medalha = '🥈';
        else if (index === 2) medalha = '🥉';
        else medalha = `${index + 1}°`;

        const foto = _avatarCell(op.imagem, op.login, '#7e3d97');
        const corMeta = percMeta >= 100 ? 'var(--emerald)' : 'var(--purple-main)';

        const progressoHtml = `
            <div class="table-progress-container">
                <div class="table-progress-bar">
                    <div class="table-progress-fill purple" style="width: ${Math.min(percMeta, 100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color: ${corMeta};">${percMeta.toFixed(1)}%</span>
            </div>
        `;

        const projecaoProgressoHtml = `
            <div class="table-progress-container">
                <div class="table-progress-bar">
                    <div class="table-progress-fill purple" style="width: ${Math.min(projecaoPct, 100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color: ${corTextoNeutro};">${projecaoPct.toFixed(1)}%</span>
            </div>
        `;

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;font-weight:600;font-size:14px;">${medalha}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-3 sticky-col-name" style="text-align:center;padding:8px 10px;font-weight:600;color:var(--purple-main);">${op.login || '-'}</td>
                <td style="text-align:center;padding:8px 10px;">${op.turno || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;white-space:nowrap;">${op.tempo_casa || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;">${formatarMoeda(op.faturamento || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.feito_dia || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.meta || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${progressoHtml}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};">${formatarMoeda(falta70)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};">${formatarMoeda(falta80)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};">${formatarMoeda(falta90)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};font-weight:700;">${formatarMoeda(falta100)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:${corTextoNeutro};">${formatarMoeda(faltaRanking)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;color:${corTextoNeutro};">${formatarMoeda(projecao)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;">${projecaoProgressoHtml}</td>
            </tr>
        `;
    }).join('');

    // Linha de Total SEMEAR
    const totalFat = operadores.reduce((s, op) => s + (op.faturamento || 0), 0);
    const totalMeta = operadores.reduce((s, op) => s + (op.meta || 0), 0);
    const totalMetaRanking = operadores.reduce((s, op) => s + (op.meta_ranking || 0), 0);
    const totalPerc = totalMeta > 0 ? (totalFat / totalMeta) * 100 : 0;
    const totalProjecao = operadores.reduce((op_s, op) => {
        const diasOp = op.dias_trabalhados || diasPassados;
        const proj = op.projecao !== undefined ? op.projecao
            : (diasOp > 0 ? ((op.faturamento || 0) / diasOp) * (op.total_dias_uteis || totalDiasMes) : 0);
        return op_s + proj;
    }, 0);
    const totalProjecaoPct = totalMeta > 0 ? (totalProjecao / totalMeta) * 100 : 0;

    const progressoTotalHtml = `
        <div class="table-progress-container">
            <div class="table-progress-bar">
                <div class="table-progress-fill purple" style="width: ${Math.min(totalPerc, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: #4a1d8c;">${totalPerc.toFixed(1)}%</span>
        </div>
    `;

    const totalProjecaoProgressoHtml = `
        <div class="table-progress-container">
            <div class="table-progress-bar">
                <div class="table-progress-fill purple" style="width: ${Math.min(totalProjecaoPct, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: #374151;">${totalProjecaoPct.toFixed(1)}%</span>
        </div>
    `;

    const tr = `
        <tr style="background:#e9d8fd;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#4a1d8c;" colspan="2"><strong>TOTAL</strong></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#4a1d8c;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#4a1d8c;">${formatarMoeda(totalFat)}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#4a1d8c;">${formatarMoeda(totalMeta)}</td>
            <td style="text-align:center;padding:10px;">${progressoTotalHtml}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#374151;">${formatarMoeda(Math.max(0, totalMeta - totalFat))}</td>
            <td style="text-align:center;padding:10px;color:#374151;">${formatarMoeda(Math.max(0, totalMetaRanking - totalFat))}</td>
            <td style="text-align:center;padding:10px;color:#374151;font-weight:700;">${formatarMoeda(totalProjecao)}</td>
            <td style="text-align:center;padding:10px;">${totalProjecaoProgressoHtml}</td>
        </tr>
    `;
    tbody.innerHTML += tr;
}

// ================================================================
// RENDERIZAÇÃO - RANKING AGORACRED (COM FOTO)
// ================================================================

function renderizarRankingAgoracred(operadores) {
    const tbody = document.getElementById('tabela-adm-agoracred');
    if (!tbody) return;

    if (!operadores || operadores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="16" style="text-align:center;color:#6B7280;padding:30px;">Nenhum operador encontrado</td></tr>';
        return;
    }

    // Ordena por faturamento (decrescente)
    operadores.sort((a, b) => (b.faturamento || 0) - (a.faturamento || 0));

    const diasPassados = operadores[0] ? (operadores[0].dias_trabalhados || 1) : 1;
    const totalDiasMes = operadores[0] ? (operadores[0].total_dias_uteis || 1) : 1;

    tbody.innerHTML = operadores.map((op, index) => {
        const percMeta = op.meta > 0 ? ((op.faturamento || 0) / op.meta) * 100 : 0;
        const falta70 = Math.max(0, (op.meta * 0.7) - (op.faturamento || 0));
        const falta80 = Math.max(0, (op.meta * 0.8) - (op.faturamento || 0));
        const falta90 = Math.max(0, (op.meta * 0.9) - (op.faturamento || 0));
        const falta100 = Math.max(0, op.meta - (op.faturamento || 0));

        // Calcula falta meta ranking específica
        const metaRankingVal = op.meta_ranking || 0;
        const faltaRanking = Math.max(0, metaRankingVal - (op.faturamento || 0));

        const diasOp = op.dias_trabalhados || diasPassados;
        const projecao = op.projecao !== undefined ? op.projecao
            : (diasOp > 0 ? ((op.faturamento || 0) / diasOp) * (op.total_dias_uteis || totalDiasMes) : 0);
        const projecaoPct = op.meta > 0 ? (projecao / op.meta) * 100 : 0;
        const corTextoNeutro = '#374151'; // Preto acinzentado conforme solicitado

        let medalha = '';
        if (index === 0) medalha = '🥇';
        else if (index === 1) medalha = '🥈';
        else if (index === 2) medalha = '🥉';
        else medalha = `${index + 1}°`;

        const foto = _avatarCell(op.imagem, op.login, '#10B981');
        const corMeta = percMeta >= 100 ? 'var(--emerald)' : 'var(--text-main)';

        const progressoHtml = `
            <div class="table-progress-container">
                <div class="table-progress-bar">
                    <div class="table-progress-fill green" style="width: ${Math.min(percMeta, 100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color: ${corMeta};">${percMeta.toFixed(1)}%</span>
            </div>
        `;

        const projecaoProgressoHtml = `
            <div class="table-progress-container">
                <div class="table-progress-bar">
                    <div class="table-progress-fill green" style="width: ${Math.min(projecaoPct, 100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color: ${corTextoNeutro};">${projecaoPct.toFixed(1)}%</span>
            </div>
        `;

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;font-weight:600;font-size:14px;">${medalha}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-3 sticky-col-name" style="text-align:center;padding:8px 10px;font-weight:600;color:var(--emerald);">${op.login || '-'}</td>
                <td style="text-align:center;padding:8px 10px;">${op.turno || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;white-space:nowrap;">${op.tempo_casa || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;">${formatarMoeda(op.faturamento || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.feito_dia || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.meta || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${progressoHtml}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};">${formatarMoeda(falta70)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};">${formatarMoeda(falta80)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};">${formatarMoeda(falta90)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corTextoNeutro};font-weight:700;">${formatarMoeda(falta100)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:${corTextoNeutro};">${formatarMoeda(faltaRanking)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;color:${corTextoNeutro};">${formatarMoeda(projecao)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;">${projecaoProgressoHtml}</td>
            </tr>
        `;
    }).join('');

    // Linha de Total AGORACRED
    const totalFat = operadores.reduce((s, op) => s + (op.faturamento || 0), 0);
    const totalMeta = operadores.reduce((s, op) => s + (op.meta || 0), 0);
    const totalMetaRanking = operadores.reduce((s, op) => s + (op.meta_ranking || 0), 0);
    const totalPerc = totalMeta > 0 ? (totalFat / totalMeta) * 100 : 0;
    const totalProjecao = operadores.reduce((op_s, op) => {
        const diasOp = op.dias_trabalhados || diasPassados;
        const proj = op.projecao !== undefined ? op.projecao
            : (diasOp > 0 ? ((op.faturamento || 0) / diasOp) * (op.total_dias_uteis || totalDiasMes) : 0);
        return op_s + proj;
    }, 0);
    const totalProjecaoPct = totalMeta > 0 ? (totalProjecao / totalMeta) * 100 : 0;

    const progressoTotalHtml = `
        <div class="table-progress-container">
            <div class="table-progress-bar">
                <div class="table-progress-fill green" style="width: ${Math.min(totalPerc, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: #065f46;">${totalPerc.toFixed(1)}%</span>
        </div>
    `;

    const totalProjecaoProgressoHtml = `
        <div class="table-progress-container">
            <div class="table-progress-bar">
                <div class="table-progress-fill green" style="width: ${Math.min(totalProjecaoPct, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: #374151;">${totalProjecaoPct.toFixed(1)}%</span>
        </div>
    `;

    const tr = `
        <tr style="background:#d1fae5;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#065f46;" colspan="2"><strong>TOTAL</strong></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#065f46;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#065f46;">${formatarMoeda(totalFat)}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#065f46;">${formatarMoeda(totalMeta)}</td>
            <td style="text-align:center;padding:10px;">${progressoTotalHtml}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#374151;">${formatarMoeda(Math.max(0, totalMeta - totalFat))}</td>
            <td style="text-align:center;padding:10px;color:#374151;">${formatarMoeda(Math.max(0, totalMetaRanking - totalFat))}</td>
            <td style="text-align:center;padding:10px;color:#374151;font-weight:700;">${formatarMoeda(totalProjecao)}</td>
            <td style="text-align:center;padding:10px;">${totalProjecaoProgressoHtml}</td>
        </tr>
    `;
    tbody.innerHTML += tr;
}

// ================================================================
// RENDERIZAÇÃO - FAIXAS SEMEAR (COM FOTO)
// ================================================================

function renderizarFaixasSemear(faixas) {
    const tbody = document.getElementById('tabela-faixas-semear');
    if (!tbody) return;

    if (!faixas || faixas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="14" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
        return;
    }

    // Colunas de fases (em ordem)
    const colunasFases = [
        'Fase 10 a 30', 'Fase 31 a 60', 'Fase 61 a 90', 'Fase 91 a 120',
        'Fase 121 a 180', 'Fase 181 a 240', 'Fase 241 a 360',
        'Fase 361 a 720', 'Fase 721 a 1080', 'Fase 1081 a 1440',
        'Fase 1441 a 1800', '> 1800'
    ];

    tbody.innerHTML = faixas.map(op => {
        const foto = _avatarCell(op.imagem, op.operador, '#7e3d97');
        let html = `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-2 sticky-col-name" style="text-align:center;padding:8px 10px;font-weight:600;color:var(--purple-main);">${op.operador || '-'}</td>
        `;

        colunasFases.forEach(fase => {
            const valor = op[fase] || 0;
            const cor = valor > 0 ? 'var(--text-main)' : '#9ca3af';
            html += `<td class="faixa-atraso-col" style="color:${cor};">${formatarMoeda(valor)}</td>`;
        });

        html += `</tr>`;
        return html;
    }).join('');

    // Cálculo dos totais de faixas
    const totaisFases = {};
    colunasFases.forEach(fase => {
        totaisFases[fase] = faixas.reduce((sum, op) => sum + (op[fase] || 0), 0);
    });

    let totalHtml = `
        <tr class="sticky-total-row" style="background:#e9d8fd;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#4a1d8c;"><strong>TOTAL</strong></td>
            <td class="sticky-col-2" style="text-align:center;padding:10px;color:#4a1d8c;"></td>
    `;
    colunasFases.forEach(fase => {
        const val = totaisFases[fase];
        totalHtml += `<td class="faixa-atraso-col" style="color:#4a1d8c;font-weight:700;">${formatarMoeda(val)}</td>`;
    });
    totalHtml += `</tr>`;
    tbody.innerHTML += totalHtml;
}

// ================================================================
// PAGAMENTOS ADM — Carregamento com Filtros e Paginação
// ================================================================

let _pagamentosAdmData = [];
let _pagAdmPage = 1;
const _pagAdmPerPage = 50;

async function carregarPagamentosAdm() {
    const tbody = document.getElementById('tabela-pagamentos-adm-individual');
    const resumoEl = document.getElementById('pag-adm-resumo');
    const totalEl = document.getElementById('pag-adm-total-registros');
    if (!tbody) return;

    const mes = document.getElementById('filtro-pag-mes-adm')?.value || getMesAtual();
    const ano = document.getElementById('filtro-pag-ano-adm')?.value || getAnoAtual();
    const banco = document.getElementById('filtro-pag-banco-adm')?.value || 'TODOS';
    const operador = document.getElementById('filtro-pag-operador-adm')?.value || 'TODOS';
    const dataInicio = document.getElementById('filtro-pag-inicio-adm')?.value || '';
    const dataFim = document.getElementById('filtro-pag-fim-adm')?.value || '';

    // AGORACRED não tem faixa de atraso — some com o filtro quando selecionado
    const filtroFaseGrp = document.getElementById('filtro-pag-fase-adm')?.closest('.filter-group');
    if (filtroFaseGrp) {
        if (banco === 'AGORACRED') {
            filtroFaseGrp.style.display = 'none';
            const faseSel = document.getElementById('filtro-pag-fase-adm');
            if (faseSel) faseSel.value = '';
        } else {
            filtroFaseGrp.style.display = 'flex';
        }
    }

    const atividade = document.getElementById('filtro-pag-atividade-adm')?.value || 'ATIVO';

    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;"><i class="fas fa-spinner fa-spin"></i> Carregando...</td></tr>';

    try {
        let url = `/api/pagamentos-adm?mes=${mes}&ano=${ano}&banco=${banco}&operador=${encodeURIComponent(operador)}&atividade=${atividade}`;
        if (dataInicio) url += `&data_inicio=${dataInicio}`;
        if (dataFim) url += `&data_fim=${dataFim}`;

        const resp = await fetch(url);
        const data = await resp.json();

        if (data.success) {
            _pagamentosAdmData = data.data || [];
            _pagAdmPage = 1;

            // Preenche dropdown de operadores na página de pagamentos
            _preencherOperadoresPagAdm(data.operadores || []);

            // Resumo rápido
            if (resumoEl) {
                const totalFat = _pagamentosAdmData.reduce((s, p) => s + (p.valorTotal || 0), 0);
                resumoEl.innerHTML = `
                    <div style="background:linear-gradient(135deg,#7e3d97,#a855f7);color:white;border-radius:12px;padding:12px 20px;flex:1;">
                        <div style="font-size:11px;opacity:0.8;text-transform:uppercase;margin-bottom:4px;">Total Faturamento</div>
                        <div style="font-size:22px;font-weight:700;">${formatarMoeda(totalFat)}</div>
                    </div>
                    <div style="background:linear-gradient(135deg,#0891b2,#22d3ee);color:white;border-radius:12px;padding:12px 20px;flex:1;">
                        <div style="font-size:11px;opacity:0.8;text-transform:uppercase;margin-bottom:4px;">Qtd. Pagamentos</div>
                        <div style="font-size:22px;font-weight:700;">${_pagamentosAdmData.length}</div>
                    </div>
                    <div style="background:linear-gradient(135deg,#10B981,#34d399);color:white;border-radius:12px;padding:12px 20px;flex:1;">
                        <div style="font-size:11px;opacity:0.8;text-transform:uppercase;margin-bottom:4px;">Ticket Médio</div>
                        <div style="font-size:22px;font-weight:700;">${_pagamentosAdmData.length > 0 ? formatarMoeda(totalFat / _pagamentosAdmData.length) : 'R$ 0,00'}</div>
                    </div>
                `;
            }

            _renderizarPagamentosAdmTabela();
        } else {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#e74c3c;padding:20px;">Erro: ${data.message || 'desconhecido'}</td></tr>`;
        }
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#e74c3c;padding:20px;">Erro de conexão ao carregar pagamentos.</td></tr>';
        console.error('[PAG ADM]', err);
    }
}

function _preencherOperadoresPagAdm(operadores) {
    const sel = document.getElementById('filtro-pag-operador-adm');
    if (!sel) return;
    const cur = sel.value;
    sel.innerHTML = '<option value="TODOS">Todos os Operadores</option>';
    operadores.forEach(op => {
        const opt = document.createElement('option');
        opt.value = op;
        opt.textContent = op;
        if (op === cur) opt.selected = true;
        sel.appendChild(opt);
    });
}

function filtrarTabelaPagamentosAdm() {
    _pagAdmPage = 1;
    _renderizarPagamentosAdmTabela();
}

function _renderizarPagamentosAdmTabela() {
    const tbody = document.getElementById('tabela-pagamentos-adm-individual');
    const totalEl = document.getElementById('pag-adm-total-registros');
    const pagEl = document.getElementById('pag-adm-pagination');
    if (!tbody) return;

    const busca = (document.getElementById('filtro-pag-busca-adm')?.value || '').toLowerCase();
    const fase = document.getElementById('filtro-pag-fase-adm')?.value || '';

    let filtrados = _pagamentosAdmData;
    if (busca) filtrados = filtrados.filter(p => (p.cliente||'').toLowerCase().includes(busca) || (p.contrato||'').toLowerCase().includes(busca));
    if (fase) filtrados = filtrados.filter(p => (p.faseAtraso || '') === fase);

    if (totalEl) totalEl.textContent = `${filtrados.length} registros`;

    const total = filtrados.length;
    const totalPages = Math.max(1, Math.ceil(total / _pagAdmPerPage));
    _pagAdmPage = Math.min(_pagAdmPage, totalPages);
    const inicio = (_pagAdmPage - 1) * _pagAdmPerPage;
    const pagina = filtrados.slice(inicio, inicio + _pagAdmPerPage);

    if (pagina.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#6B7280;padding:30px;">Nenhum pagamento encontrado com os filtros aplicados.</td></tr>';
    } else {
        tbody.innerHTML = pagina.map(p => {
            const bancoCor = (p.banco || '') === 'SEMEAR' ? '#7e3d97' : '#10B981';
            return `
                <tr>
                    <td style="padding:8px 10px;text-align:center;font-size:12px;white-space:nowrap;">${formatarData(p.dtPgto) || '-'}</td>
                    <td style="padding:8px 10px;text-align:center;font-weight:600;">${p.contrato || '-'}</td>
                    <td style="padding:8px 10px;text-align:left;">${p.cliente || '-'}</td>
                    <td style="padding:8px 10px;text-align:center;">
                        <span style="background:${bancoCor};color:white;padding:1px 8px;border-radius:10px;font-size:10px;font-weight:600;">${p.banco || '-'}</span>
                    </td>
                    <td style="padding:8px 10px;text-align:center;font-size:12px;">${p.operador || p.login || '-'}</td>
                    <td style="padding:8px 10px;text-align:center;font-size:11px;color:var(--text-muted);">${(p.banco === 'AGORACRED') ? '—' : (p.faseAtraso || '-')}</td>
                    <td style="padding:8px 10px;text-align:center;font-weight:700;">${formatarMoeda(p.valorTotal || 0)}</td>
                </tr>
            `;
        }).join('');
    }

    // Paginação
    if (pagEl) {
        if (totalPages <= 1) { pagEl.innerHTML = ''; return; }
        let html = '';
        const prev = _pagAdmPage > 1;
        const next = _pagAdmPage < totalPages;
        html += `<button onclick="_pagAdmIr(${_pagAdmPage-1})" ${prev?'':'disabled'} style="padding:4px 10px;border-radius:6px;border:1px solid #d1d5db;cursor:${prev?'pointer':'not-allowed'};background:${prev?'white':'#f3f4f6'};">‹</button>`;
        const start = Math.max(1, _pagAdmPage - 2);
        const end = Math.min(totalPages, _pagAdmPage + 2);
        for (let i = start; i <= end; i++) {
            html += `<button onclick="_pagAdmIr(${i})" style="padding:4px 10px;border-radius:6px;border:1px solid ${i===_pagAdmPage?'var(--purple-main)':'#d1d5db'};background:${i===_pagAdmPage?'var(--purple-main)':'white'};color:${i===_pagAdmPage?'white':'inherit'};font-weight:${i===_pagAdmPage?'700':'400'};cursor:pointer;">${i}</button>`;
        }
        html += `<button onclick="_pagAdmIr(${_pagAdmPage+1})" ${next?'':'disabled'} style="padding:4px 10px;border-radius:6px;border:1px solid #d1d5db;cursor:${next?'pointer':'not-allowed'};background:${next?'white':'#f3f4f6'};">›</button>`;
        html += `<span style="font-size:12px;color:var(--text-muted);margin-left:8px;">${inicio+1}–${Math.min(inicio+_pagAdmPerPage,total)} de ${total}</span>`;
        pagEl.innerHTML = html;
    }
}

function _pagAdmIr(p) {
    _pagAdmPage = p;
    _renderizarPagamentosAdmTabela();
}

window.carregarPagamentosAdm = carregarPagamentosAdm;
window.filtrarTabelaPagamentosAdm = filtrarTabelaPagamentosAdm;
window._pagAdmIr = _pagAdmIr;


// ================================================================
// RENDERIZAÇÃO - EVOLUÇÃO OPERADORES
// ================================================================

function renderizarEvolucaoOperadores(operadores) {
    const tbody = document.getElementById('tabela-evolucao-operadores-adm');
    const resumo = document.getElementById('resumo-evolucao-adm');

    if (!tbody) return;

    if (!operadores || operadores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
        if (resumo) resumo.innerHTML = '';
        return;
    }

    const positivos = operadores.filter(op => (op.variacao_percentual || 0) > 0);
    const negativos = operadores.filter(op => (op.variacao_percentual || 0) < 0);

    if (resumo) {
        resumo.innerHTML = `
            <div style="background:#f3e8ff;color:#612d75;padding:12px 16px;border-radius:8px;font-weight:600;margin-bottom:16px;">
                <strong>${positivos.length} operadores com faturamento acima do período anterior</strong>
                <span style="margin-left:20px;color:#991b1b;">
                    ${negativos.length} operadores com faturamento abaixo do período anterior.
                </span>
            </div>
        `;
    }

    operadores.sort((a, b) => (b.variacao_percentual || 0) - (a.variacao_percentual || 0));

    tbody.innerHTML = operadores.map(op => {
        const corVar = (op.variacao_percentual || 0) >= 0 ? 'var(--emerald)' : '#e74c3c';
        const sinal = (op.variacao_percentual || 0) >= 0 ? '+' : '';

        const bancoCor = op.banco === 'SEMEAR' ? '#7e3d97' : '#10B981';
        const bancoLabel = op.banco === 'SEMEAR' ? 'SEMEAR' : 'AGORACRED';
        const foto = _avatarCell(op.imagem, op.operador, bancoCor);

        // VAR. Atingido da Meta: variacao_meta_pp / perc_meta_anterior * 100
        const percMetaAnt = op.perc_meta_anterior || 0;
        const varAtingPct = percMetaAnt > 0
            ? ((op.perc_meta_atual - percMetaAnt) / percMetaAnt) * 100
            : 0;
        const corVarAting = varAtingPct >= 0 ? 'var(--emerald)' : '#e74c3c';
        const sinalVarAting = varAtingPct >= 0 ? '+' : '';

        const corMeta = (op.perc_meta_atual || 0) >= 100 ? 'var(--emerald)' : 'var(--text-main)';
        
        // Barras de progresso nas células
        const progressoAtualHtml = `
            <div class="table-progress-container" style="min-width:110px;">
                <div class="table-progress-bar">
                    <div class="table-progress-fill ${op.banco === 'SEMEAR' ? 'purple' : 'green'}" style="width: ${Math.min(op.perc_meta_atual || 0, 100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color: ${bancoCor};">${(op.perc_meta_atual || 0).toFixed(1)}%</span>
            </div>
        `;

        const progressoAntHtml = `
            <div class="table-progress-container" style="min-width:110px;">
                <div class="table-progress-bar">
                    <div class="table-progress-fill ${op.banco === 'SEMEAR' ? 'purple' : 'green'}" style="width: ${Math.min(percMetaAnt, 100)}%; opacity: 0.6;"></div>
                </div>
                <span class="table-progress-text" style="color: var(--text-muted);">${percMetaAnt.toFixed(1)}%</span>
            </div>
        `;

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 10px;">
                    <span style="background:${bancoCor};color:white;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">${bancoLabel}</span>
                </td>
                <td class="sticky-col-3 sticky-col-name" style="text-align:center;padding:8px 10px;font-weight:600;">${op.operador || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;">${formatarMoeda(op.fat_atual || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.fat_anterior || 0)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corVar};font-weight:700;">${formatarMoeda(op.variacao || 0)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corVar};font-weight:700;">${sinal}${(op.variacao_percentual || 0).toFixed(1)}%</td>
                <td style="text-align:center;padding:8px 10px;">${progressoAtualHtml}</td>
                <td style="text-align:center;padding:8px 10px;">${progressoAntHtml}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:${(op.variacao_meta_pp || 0) >= 0 ? 'var(--emerald)' : '#e74c3c'};">${(op.variacao_meta_pp || 0) >= 0 ? '+' : ''}${(op.variacao_meta_pp || 0).toFixed(1)} pp</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:${corVarAting};">${sinalVarAting}${varAtingPct.toFixed(1)}%</td>
            </tr>
        `;
    }).join('');

    // Linha de total
    const totalFatAtual = operadores.reduce((s, op) => s + (op.fat_atual || 0), 0);
    const totalFatAnt = operadores.reduce((s, op) => s + (op.fat_anterior || 0), 0);
    const variacaoTotal = totalFatAnt > 0 ? ((totalFatAtual - totalFatAnt) / totalFatAnt) * 100 : 0;
    const difTotal = totalFatAtual - totalFatAnt;
    const corVarTotal = variacaoTotal >= 0 ? 'var(--emerald)' : '#e74c3c';
    tbody.innerHTML += `
        <tr style="background:#fef3c7;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#92400e;"></td>
            <td class="sticky-col-2" style="text-align:center;padding:10px;color:#92400e;"></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#92400e;"><strong>TOTAL</strong></td>
            <td style="text-align:center;padding:10px;color:#92400e;">${formatarMoeda(totalFatAtual)}</td>
            <td style="text-align:center;padding:10px;color:#92400e;">${formatarMoeda(totalFatAnt)}</td>
            <td style="text-align:center;padding:10px;color:${corVarTotal};">${formatarMoeda(difTotal)}</td>
            <td style="text-align:center;padding:10px;color:${corVarTotal};">${variacaoTotal >= 0 ? '+' : ''}${variacaoTotal.toFixed(1)}%</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
        </tr>
    `;
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