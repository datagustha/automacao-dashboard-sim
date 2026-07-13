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

    // Rodapé SEMEAR — duas colunas: Mês Anterior | Diferença da Meta
    const corVarSemear = variacaoSemear >= 0 ? '#16a34a' : '#dc2626';
    const bgVarSemear = variacaoSemear >= 0 ? '#dcfce7' : '#fee2e2';
    const setaSemear = variacaoSemear >= 0 ? '▲' : '▼';
    const faltaSemearHtml = faltaSemear > 0
        ? `<span style="font-weight:700;color:var(--text-main);font-size:12px;">Falta: ${formatarMoeda(faltaSemear)}</span>
           <span style="color:#d97706;background:#fef3c7;padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:4px;">${faltaSemearPct.toFixed(1)}% abaixo</span>`
        : `<span style="font-weight:700;color:#16a34a;font-size:12px;">Meta Atingida! 🎉</span>`;

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

    // Rodapé AGORACRED — duas colunas
    const corVarAgoracred = variacaoAgoracred >= 0 ? '#16a34a' : '#dc2626';
    const bgVarAgoracred = variacaoAgoracred >= 0 ? '#dcfce7' : '#fee2e2';
    const setaAgoracred = variacaoAgoracred >= 0 ? '▲' : '▼';
    const faltaAgoracredHtml = faltaAgoracred > 0
        ? `<span style="font-weight:700;color:var(--text-main);font-size:12px;">Falta: ${formatarMoeda(faltaAgoracred)}</span>
           <span style="color:#d97706;background:#fef3c7;padding:2px 6px;border-radius:4px;font-weight:700;font-size:11px;margin-left:4px;">${faltaAgoracredPct.toFixed(1)}% abaixo</span>`
        : `<span style="font-weight:700;color:#16a34a;font-size:12px;">Meta Atingida! 🎉</span>`;

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
    // CARDS - Linha 2: Operações e Ticket (4 cards)
    // ============================================================
    const totalOps = dados.total_operacoes || 0;
    const opsAnterior = dados.operacoes_anterior || 0;

    document.getElementById('kpi-total-ops-adm').textContent = totalOps;
    document.getElementById('kpi-ops-adm-anterior').textContent = `← Mês anterior: ${opsAnterior}`;

    document.getElementById('kpi-ticket-adm').textContent = formatarMoeda(dados.ticket_medio || 0);
    const ticketAdmAntEl = document.getElementById('kpi-ticket-adm-anterior');
    if (ticketAdmAntEl) {
        ticketAdmAntEl.textContent = `← Mês anterior: ${formatarMoeda(dados.ticket_medio_anterior || 0)}`;
    }

    // Operações SEMEAR
    const opsSemear = semear.operacoes || 0;
    const opsSemearAnt = semear.operacoes_anterior || 0;
    document.getElementById('kpi-ops-semear').textContent = opsSemear;
    document.getElementById('kpi-ops-semear-anterior').textContent = `← Mês anterior: ${opsSemearAnt}`;

    // Operações AGORACRED
    const opsAgoracred = agoracred.operacoes || 0;
    const opsAgoracredAnt = agoracred.operacoes_anterior || 0;
    document.getElementById('kpi-ops-agoracred').textContent = opsAgoracred;
    document.getElementById('kpi-ops-agoracred-anterior').textContent = `← Mês anterior: ${opsAgoracredAnt}`;

    // Ticket Médio SEMEAR
    const ticketSemearEl = document.getElementById('kpi-ticket-semear');
    const ticketSemearAntEl = document.getElementById('kpi-ticket-semear-anterior');
    if (ticketSemearEl) {
        ticketSemearEl.textContent = formatarMoeda(semear.ticket_medio || 0);
    }
    if (ticketSemearAntEl) {
        ticketSemearAntEl.textContent = `← Mês anterior: ${formatarMoeda(semear.ticket_medio_anterior || 0)}`;
    }

    // Ticket Médio AGORACRED
    const ticketAgoracredEl = document.getElementById('kpi-ticket-agoracred');
    const ticketAgoracredAntEl = document.getElementById('kpi-ticket-agoracred-anterior');
    if (ticketAgoracredEl) {
        ticketAgoracredEl.textContent = formatarMoeda(agoracred.ticket_medio || 0);
    }
    if (ticketAgoracredAntEl) {
        ticketAgoracredAntEl.textContent = `← Mês anterior: ${formatarMoeda(agoracred.ticket_medio_anterior || 0)}`;
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
            <td style="padding:10px 14px;text-align:center;color:#4a1d8c;"><strong>📊 TOTAL DO PERÍODO</strong></td>
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
        tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;color:#6B7280;padding:30px;">Nenhum operador encontrado</td></tr>';
        return;
    }

    // Ordena por faturamento (decrescente)
    operadores.sort((a, b) => (b.faturamento || 0) - (a.faturamento || 0));

    tbody.innerHTML = operadores.map((op, index) => {
        const percMeta = op.meta > 0 ? ((op.faturamento || 0) / op.meta) * 100 : 0;
        const falta70 = Math.max(0, (op.meta * 0.7) - (op.faturamento || 0));
        const falta80 = Math.max(0, (op.meta * 0.8) - (op.faturamento || 0));
        const falta90 = Math.max(0, (op.meta * 0.9) - (op.faturamento || 0));
        const falta100 = Math.max(0, op.meta - (op.faturamento || 0));

        let medalha = '';
        if (index === 0) medalha = '🥇';
        else if (index === 1) medalha = '🥈';
        else if (index === 2) medalha = '🥉';
        else medalha = `${index + 1}°`;

        const foto = _avatarCell(op.imagem, op.login, '#7e3d97');
        const corMeta = percMeta >= 100 ? 'var(--emerald)' : 'var(--text-main)';

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;font-weight:600;font-size:14px;">${medalha}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-3" style="text-align:center;padding:8px 10px;font-weight:600;color:var(--purple-main);">${op.login || '-'}</td>
                <td style="text-align:center;padding:8px 10px;">${op.turno || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;white-space:nowrap;">${op.tempo_casa || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;">${formatarMoeda(op.faturamento || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.feito_dia || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.meta || 0)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;color:${corMeta};">${percMeta.toFixed(1)}%</td>
                <td style="text-align:center;padding:8px 10px;color:#e74c3c;">${formatarMoeda(falta70)}</td>
                <td style="text-align:center;padding:8px 10px;color:#e74c3c;">${formatarMoeda(falta80)}</td>
                <td style="text-align:center;padding:8px 10px;color:#e74c3c;">${formatarMoeda(falta90)}</td>
                <td style="text-align:center;padding:8px 10px;color:#7c3aed;font-weight:700;">${formatarMoeda(falta100)}</td>
            </tr>
        `;
    }).join('');

    // Linha de Total SEMEAR
    const totalFat = operadores.reduce((s, op) => s + (op.faturamento || 0), 0);
    const totalMeta = operadores.reduce((s, op) => s + (op.meta || 0), 0);
    const totalPerc = totalMeta > 0 ? (totalFat / totalMeta) * 100 : 0;
    const tr = `
        <tr style="background:#e9d8fd;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#4a1d8c;" colspan="2"><strong>📊 TOTAL</strong></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#4a1d8c;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#4a1d8c;">${formatarMoeda(totalFat)}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#4a1d8c;">${formatarMoeda(totalMeta)}</td>
            <td style="text-align:center;padding:10px;color:#4a1d8c;font-weight:700;">${totalPerc.toFixed(1)}%</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#7c3aed;">${formatarMoeda(Math.max(0, totalMeta - totalFat))}</td>
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
        tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;color:#6B7280;padding:30px;">Nenhum operador encontrado</td></tr>';
        return;
    }

    // Ordena por faturamento (decrescente)
    operadores.sort((a, b) => (b.faturamento || 0) - (a.faturamento || 0));

    tbody.innerHTML = operadores.map((op, index) => {
        const percMeta = op.meta > 0 ? ((op.faturamento || 0) / op.meta) * 100 : 0;
        const falta70 = Math.max(0, (op.meta * 0.7) - (op.faturamento || 0));
        const falta80 = Math.max(0, (op.meta * 0.8) - (op.faturamento || 0));
        const falta90 = Math.max(0, (op.meta * 0.9) - (op.faturamento || 0));
        const falta100 = Math.max(0, op.meta - (op.faturamento || 0));

        let medalha = '';
        if (index === 0) medalha = '🥇';
        else if (index === 1) medalha = '🥈';
        else if (index === 2) medalha = '🥉';
        else medalha = `${index + 1}°`;

        const foto = _avatarCell(op.imagem, op.login, '#10B981');
        const corMeta = percMeta >= 100 ? 'var(--emerald)' : 'var(--text-main)';

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;font-weight:600;font-size:14px;">${medalha}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-3" style="text-align:center;padding:8px 10px;font-weight:600;color:var(--emerald);">${op.login || '-'}</td>
                <td style="text-align:center;padding:8px 10px;">${op.turno || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-size:11px;white-space:nowrap;">${op.tempo_casa || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;">${formatarMoeda(op.faturamento || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.feito_dia || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.meta || 0)}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:700;color:${corMeta};">${percMeta.toFixed(1)}%</td>
                <td style="text-align:center;padding:8px 10px;color:#e74c3c;">${formatarMoeda(falta70)}</td>
                <td style="text-align:center;padding:8px 10px;color:#e74c3c;">${formatarMoeda(falta80)}</td>
                <td style="text-align:center;padding:8px 10px;color:#e74c3c;">${formatarMoeda(falta90)}</td>
                <td style="text-align:center;padding:8px 10px;color:#059669;font-weight:700;">${formatarMoeda(falta100)}</td>
            </tr>
        `;
    }).join('');

    // Linha de Total AGORACRED
    const totalFat = operadores.reduce((s, op) => s + (op.faturamento || 0), 0);
    const totalMeta = operadores.reduce((s, op) => s + (op.meta || 0), 0);
    const totalPerc = totalMeta > 0 ? (totalFat / totalMeta) * 100 : 0;
    const tr = `
        <tr style="background:#d1fae5;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#065f46;" colspan="2"><strong>📊 TOTAL</strong></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#065f46;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#065f46;">${formatarMoeda(totalFat)}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#065f46;">${formatarMoeda(totalMeta)}</td>
            <td style="text-align:center;padding:10px;color:#065f46;font-weight:700;">${totalPerc.toFixed(1)}%</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#059669;">${formatarMoeda(Math.max(0, totalMeta - totalFat))}</td>
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
        tbody.innerHTML = '<tr><td colspan="15" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
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
                <td style="text-align:center;padding:8px 10px;">${foto}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;">${op.operador || '-'}</td>
        `;

        colunasFases.forEach(fase => {
            const valor = op[fase] || 0;
            const cor = valor > 0 ? 'var(--text-main)' : '#9ca3af';
            html += `<td style="text-align:center;padding:8px 10px;font-size:13px;color:${cor};">${formatarMoeda(valor)}</td>`;
        });

        html += `</tr>`;
        return html;
    }).join('');
}

// ================================================================
// RENDERIZAÇÃO - EVOLUÇÃO OPERADORES
// ================================================================

function renderizarEvolucaoOperadores(operadores) {
    const tbody = document.getElementById('tabela-evolucao-operadores-adm');
    const resumo = document.getElementById('resumo-evolucao-adm');

    if (!tbody) return;

    if (!operadores || operadores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
        if (resumo) resumo.innerHTML = '';
        return;
    }

    const positivos = operadores.filter(op => (op.variacao_percentual || 0) > 0);
    const negativos = operadores.filter(op => (op.variacao_percentual || 0) < 0);

    if (resumo) {
        resumo.innerHTML = `
            <div style="background:#f3e8ff;color:#612d75;padding:12px 16px;border-radius:8px;font-weight:600;margin-bottom:16px;">
                <strong>📊 ${positivos.length} operadores com faturamento acima do período anterior</strong>
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
        const bancoLabel = op.banco === 'SEMEAR' ? '🟣 SEMEAR' : '🟢 AGORACRED';
        const foto = _avatarCell(op.imagem, op.operador, bancoCor);

        // VAR. Atingido da Meta: variacao_meta_pp / perc_meta_anterior * 100
        const percMetaAnt = op.perc_meta_anterior || 0;
        const varAtingPct = percMetaAnt > 0
            ? ((op.perc_meta_atual - percMetaAnt) / percMetaAnt) * 100
            : 0;
        const corVarAting = varAtingPct >= 0 ? 'var(--emerald)' : '#e74c3c';
        const sinalVarAting = varAtingPct >= 0 ? '+' : '';

        const corMeta = (op.perc_meta_atual || 0) >= 100 ? 'var(--emerald)' : 'var(--text-main)';
        const corMetaAnt = percMetaAnt >= 100 ? 'var(--emerald)' : 'var(--text-muted)';

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 10px;">
                    <span style="background:${bancoCor};color:white;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">${bancoLabel}</span>
                </td>
                <td class="sticky-col-3" style="text-align:center;padding:8px 10px;font-weight:600;">${op.operador || '-'}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;">${formatarMoeda(op.fat_atual || 0)}</td>
                <td style="text-align:center;padding:8px 10px;">${formatarMoeda(op.fat_anterior || 0)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corVar};font-weight:700;">${formatarMoeda(op.variacao || 0)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corVar};font-weight:700;">${sinal}${(op.variacao_percentual || 0).toFixed(1)}%</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:${corMeta};">${(op.perc_meta_atual || 0).toFixed(1)}%</td>
                <td style="text-align:center;padding:8px 10px;color:${corMetaAnt};">${percMetaAnt.toFixed(1)}%</td>
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
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#92400e;"><strong>📊 TOTAL</strong></td>
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