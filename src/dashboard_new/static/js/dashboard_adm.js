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

    // --- CÁLCULO E EXIBIÇÃO DE ÚLTIMO RECEBIMENTO POR BANCO ---
    const todasDatasSemear = [];
    (semear.operadores || []).forEach(op => {
        const ult = op.ultimo_pagamento || op.ultima_data;
        if (ult) todasDatasSemear.push(ult);
    });
    (semear.evolucao || []).forEach(e => { if (e.data) todasDatasSemear.push(e.data); });
    
    const recSemearEl = document.getElementById('kpi-recebimento-semear');
    if (recSemearEl) {
        if (todasDatasSemear.length > 0) {
            todasDatasSemear.sort();
            const ultD = todasDatasSemear[todasDatasSemear.length - 1];
            if (ultD && ultD.includes('-')) {
                const p = ultD.split('-');
                recSemearEl.innerHTML = `<i class="fas fa-clock" style="color:var(--purple-main);margin-right:4px;"></i>Último Recebimento: <strong>${p[2]}/${p[1]}/${p[0]}</strong>`;
            } else {
                recSemearEl.textContent = '';
            }
        } else {
            recSemearEl.textContent = 'Sem recebimentos no período';
        }
    }

    const todasDatasAgoracred = [];
    (agoracred.operadores || []).forEach(op => {
        const ult = op.ultimo_pagamento || op.ultima_data;
        if (ult) todasDatasAgoracred.push(ult);
    });
    (agoracred.evolucao || []).forEach(e => { if (e.data) todasDatasAgoracred.push(e.data); });

    const recAgoracredEl = document.getElementById('kpi-recebimento-agoracred');
    if (recAgoracredEl) {
        if (todasDatasAgoracred.length > 0) {
            todasDatasAgoracred.sort();
            const ultD = todasDatasAgoracred[todasDatasAgoracred.length - 1];
            if (ultD && ultD.includes('-')) {
                const p = ultD.split('-');
                recAgoracredEl.innerHTML = `<i class="fas fa-clock" style="color:var(--emerald);margin-right:4px;"></i>Último Recebimento: <strong>${p[2]}/${p[1]}/${p[0]}</strong>`;
            } else {
                recAgoracredEl.textContent = '';
            }
        } else {
            recAgoracredEl.textContent = 'Sem recebimentos no período';
        }
    }

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
    // Guarda dados do ranking globalmente para exportação CSV
    window._rankingAdmSemear = semear.operadores || [];

    // ============================================================
    // TABELA - Ranking AGORACRED (COM FOTOS)
    // ============================================================
    renderizarRankingAgoracred(agoracred.operadores || []);
    // Guarda dados do ranking globalmente para exportação CSV
    window._rankingAdmAgoracred = agoracred.operadores || [];

    // ============================================================
    // BANNER - Última Baixa Bancária (Feito/Dia)
    // Exibe "Baixas até dia X" acima de cada ranking, informando
    // que o feito/dia é dividido pelo dia desta data máxima do banco
    // ============================================================
    _atualizarBannerUltimaBaixa('semear', semear.ultima_baixa);
    _atualizarBannerUltimaBaixa('agoracred', agoracred.ultima_baixa);

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

    // Ordena por % meta atingida (decrescente)
    operadores.sort((a, b) => {
        const percA = a.meta > 0 ? ((a.faturamento || 0) / a.meta) * 100 : 0;
        const percB = b.meta > 0 ? ((b.faturamento || 0) / b.meta) * 100 : 0;
        return percB - percA;
    });

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

    // Ordena por % meta atingida (decrescente)
    operadores.sort((a, b) => {
        const percA = a.meta > 0 ? ((a.faturamento || 0) / a.meta) * 100 : 0;
        const percB = b.meta > 0 ? ((b.faturamento || 0) / b.meta) * 100 : 0;
        return percB - percA;
    });

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
function renderizarFaixasSemear(faixas) {
    const tbody = document.getElementById('tabela-faixas-semear');
    if (!tbody) return;

    // Guarda dados na variável global para permitir alternância de visualização instantânea
    window._faixasAdmSemear = faixas;

    if (!faixas || faixas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="14" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
        return;
    }

    // Modo de visualização ativo: 'valor' ou 'qtd'
    const modo = window._faixasModoVisualizacao || 'valor';

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
            // Se o modo for 'qtd', lemos a chave com sufixo '_qtd'
            const chave = modo === 'qtd' ? `${fase}_qtd` : fase;
            const valor = op[chave] || 0;
            const cor = valor > 0 ? 'var(--text-main)' : '#9ca3af';
            
            // Formata conforme o modo selecionado
            const valorFormatado = modo === 'qtd' ? parseInt(valor) : formatarMoeda(valor);
            html += `<td class="faixa-atraso-col" style="color:${cor};text-align:center;">${valorFormatado}</td>`;
        });

        html += `</tr>`;
        return html;
    }).join('');

    // Cálculo dos totais de faixas
    const totaisFases = {};
    colunasFases.forEach(fase => {
        const chave = modo === 'qtd' ? `${fase}_qtd` : fase;
        totaisFases[fase] = faixas.reduce((sum, op) => sum + (op[chave] || 0), 0);
    });

    let totalHtml = `
        <tr class="sticky-total-row" style="background:#e9d8fd;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#4a1d8c;"><strong>TOTAL</strong></td>
            <td class="sticky-col-2" style="text-align:center;padding:10px;color:#4a1d8c;"></td>
    `;
    colunasFases.forEach(fase => {
        const val = totaisFases[fase];
        const valFormatado = modo === 'qtd' ? parseInt(val) : formatarMoeda(val);
        totalHtml += `<td class="faixa-atraso-col" style="color:#4a1d8c;font-weight:700;text-align:center;">${valFormatado}</td>`;
    });
    totalHtml += `</tr>`;
    tbody.innerHTML += totalHtml;
}

/**
 * Altera o modo de visualização das faixas de atraso (valores R$ ou quantidade de contratos).
 * Atualiza o estado dos botões de alternância e redesenha a tabela.
 *
 * @param {string} modo - 'valor' ou 'qtd'
 */
function alterarVisualizacaoFaixas(modo) {
    window._faixasModoVisualizacao = modo;
    
    // Atualiza estados visuais dos botões de toggle
    const btnValor = document.getElementById('btn-faixa-modo-valor');
    const btnQtd = document.getElementById('btn-faixa-modo-qtd');
    
    if (btnValor && btnQtd) {
        if (modo === 'qtd') {
            btnValor.style.background = 'transparent';
            btnValor.style.color = '#4b5563';
            btnQtd.style.background = 'var(--purple-main)';
            btnQtd.style.color = 'white';
        } else {
            btnValor.style.background = 'var(--purple-main)';
            btnValor.style.color = 'white';
            btnQtd.style.background = 'transparent';
            btnQtd.style.color = '#4b5563';
        }
    }
    
    // Re-renderiza a tabela com o novo formato
    if (window._faixasAdmSemear) {
        renderizarFaixasSemear(window._faixasAdmSemear);
    }
}

window.alterarVisualizacaoFaixas = alterarVisualizacaoFaixas;

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

    // Lendo filtros globais do topo do Admin
    const mes = document.getElementById('filtro-mes-adm')?.value || getMesAtual();
    const ano = document.getElementById('filtro-ano-adm')?.value || getAnoAtual();
    const banco = document.getElementById('filtro-banco-adm')?.value || 'TODOS';
    const operador = document.getElementById('filtro-operador-adm')?.value || 'TODOS';
    const atividade = document.getElementById('filtro-activity-adm')?.value || 'ATIVO';

    const dataInicio = document.getElementById('filtro-pag-inicio-adm')?.value || '';
    const dataFim = document.getElementById('filtro-pag-fim-adm')?.value || '';

    // AGORACRED não tem faixa de atraso — oculta o multiselect de faixas do topo em caso de AGORACRED
    const multiselectFaixa = document.getElementById('multiselect-faixa-adm');
    if (multiselectFaixa) {
        if (banco === 'AGORACRED') {
            multiselectFaixa.style.display = 'none';
        } else {
            multiselectFaixa.style.display = 'flex';
        }
    }

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

            // Banner de operador filtrado na aba Pagamentos
            const bannerPag = document.getElementById('banner-pag-operador-adm');
            const bannerNome = document.getElementById('banner-pag-op-nome');
            const bannerImg = document.getElementById('banner-pag-op-avatar-img');
            const bannerTxt = document.getElementById('banner-pag-op-avatar-txt');
            if (bannerPag) {
                if (operador && operador !== 'TODOS') {
                    if (bannerNome) bannerNome.textContent = operador;
                    
                    let opImagem = '';
                    const selectPagOp = document.getElementById('filtro-pag-operador-adm');
                    if (selectPagOp) {
                        const optSel = Array.from(selectPagOp.options).find(opt => opt.value === operador);
                        if (optSel && optSel.dataset && optSel.dataset.imagem) {
                            opImagem = optSel.dataset.imagem;
                        }
                    }
                    
                    if (!opImagem && window.todosOperadoresCadastrados) {
                        const opCadastrado = window.todosOperadoresCadastrados.find(o => o.login === operador);
                        if (opCadastrado && opCadastrado.imagem) {
                            opImagem = opCadastrado.imagem;
                        }
                    }
                    
                    if (opImagem) {
                        if (bannerImg) {
                            bannerImg.src = opImagem;
                            bannerImg.style.display = 'block';
                        }
                        if (bannerTxt) bannerTxt.style.display = 'none';
                    } else {
                        if (bannerImg) bannerImg.style.display = 'none';
                        if (bannerTxt) {
                            bannerTxt.textContent = operador.replace(/[0-9]/g, '').slice(0, 2).toUpperCase() || 'OP';
                            bannerTxt.style.display = 'flex';
                        }
                    }
                    bannerPag.style.display = 'flex';
                } else {
                    bannerPag.style.display = 'none';
                }
            }

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
    const datalist = document.getElementById('datalist-operadores-pag');
    if (!sel) return;
    const cur = sel.value;
    sel.innerHTML = '<option value="TODOS">Todos os Operadores</option>';
    
    if (datalist) datalist.innerHTML = '<option value="TODOS">Todos os Operadores</option>';

    operadores.forEach(op => {
        const login = op.login;
        const imagem = op.imagem;

        const opt = document.createElement('option');
        opt.value = login;
        opt.textContent = login;
        opt.dataset.imagem = imagem || '';
        if (login === cur) opt.selected = true;
        sel.appendChild(opt);

        if (datalist) {
            const dOpt = document.createElement('option');
            dOpt.value = login;
            dOpt.textContent = login;
            datalist.appendChild(dOpt);
        }
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
    const faixa = document.getElementById('filtro-faixa-adm')?.value || 'todas';

    let filtrados = _pagamentosAdmData;
    if (busca) filtrados = filtrados.filter(p => (p.cliente||'').toLowerCase().includes(busca) || (p.contrato||'').toLowerCase().includes(busca));
    
    if (faixa !== 'todas') {
        const fasesSelecionadas = faixa.split(',').map(f => f.trim().toLowerCase());
        filtrados = filtrados.filter(p => {
            const fAtraso = (p.faseAtraso || '').trim().toLowerCase();
            return fasesSelecionadas.includes(fAtraso);
        });
    }

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

var _rankingAdmSemear = [];
var _rankingAdmAgoracred = [];

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
// BANNER - Última Baixa Bancária por Banco
// ================================================================

/**
 * Atualiza o banner "Baixas até dia X" acima do ranking do banco informado.
 * O texto informa ao gestor que o feito/dia é calculado dividindo o faturamento
 * pelo número do dia correspondente à data máxima de pagamento do banco inteiro.
 *
 * @param {string} banco - 'semear' ou 'agoracred'
 * @param {string|null} ultimaBaixa - Data no formato 'DD/MM/YYYY' ou null
 */
function _atualizarBannerUltimaBaixa(banco, ultimaBaixa) {
    // IDs dos elementos HTML criados no dashboard_adm.html
    const bannerEl = document.getElementById(`banner-ultima-baixa-${banco}`);
    const textoEl  = document.getElementById(`txt-ultima-baixa-${banco}`);
    if (!bannerEl || !textoEl) return;

    if (ultimaBaixa) {
        // Exibe o banner com a data máxima do banco
        textoEl.innerHTML = `<strong>Baixas até ${ultimaBaixa}</strong> (Feito/Dia = Faturamento ÷ ${ultimaBaixa.split('/')[0]} dias)`;
        bannerEl.style.display = 'flex';  // torna visível
    } else {
        // Oculta o banner quando não há data (ex: sem pagamentos no mês)
        bannerEl.style.display = 'none';
    }
}

// ================================================================
// EXPORT - CSV DE PAGAMENTOS
// ================================================================

/**
 * Exporta para CSV os pagamentos filtrados atualmente visíveis na tabela.
 * Os dados são lidos de _pagamentosAdmData (já em memória no JS),
 * aplicando os filtros de busca e fase exatamente como na tabela.
 * Não requer nenhuma chamada de backend.
 */
function exportarPagamentosCSV() {
    // Lê os filtros ativos para aplicar exatamente o mesmo subset da tabela
    const busca = (document.getElementById('filtro-pag-busca-adm')?.value || '').toLowerCase();
    const fase  = document.getElementById('filtro-pag-fase-adm')?.value || '';

    // Aplica os filtros sobre a lista completa de pagamentos em memória
    let dados = _pagamentosAdmData || [];
    if (busca) dados = dados.filter(p => (p.cliente||'').toLowerCase().includes(busca) || (p.contrato||'').toLowerCase().includes(busca));
    if (fase)  dados = dados.filter(p => (p.faseAtraso || '') === fase);

    if (dados.length === 0) {
        alert('Nenhum pagamento para exportar com os filtros aplicados.');
        return;
    }

    // Cabeçalhos do CSV
    const cabecalhos = ['Data Pgto', 'Contrato', 'Cliente', 'Banco', 'Operador', 'Faixa Atraso', 'Valor Total'];

    // Constrói as linhas do CSV escapando campos com vírgula
    const linhas = dados.map(p => [
        p.dtPgto || '',
        `"${(p.contrato || '').replace(/"/g, '""')}"`,
        `"${(p.cliente  || '').replace(/"/g, '""')}"`,
        p.banco || '',
        p.operador || '',
        p.faseAtraso || '',
        (p.valorTotal || 0).toFixed(2).replace('.', ',')
    ].join(';'));

    // Monta o conteúdo do CSV com BOM UTF-8 para compatibilidade com Excel
    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');

    // Cria o link de download e dispara o click automaticamente
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const dataHoje = new Date().toISOString().split('T')[0];
    link.href     = url;
    link.download = `pagamentos_${dataHoje}.csv`;
    document.body.appendChild(link);
    link.click();  // dispara download
    document.body.removeChild(link);
    URL.revokeObjectURL(url);  // libera memória
}

// ================================================================
// EXPORT - CSV DO RANKING
// ================================================================

/**
 * Exporta para CSV o ranking do banco especificado.
 * Os dados são lidos das variáveis globais _rankingAdmSemear e _rankingAdmAgoracred
 * que são preenchidas em atualizarDashboardAdm() a cada carga da API.
 *
 * @param {string} banco - 'semear' ou 'agoracred'
 */
function exportarRankingCSV(banco) {
    // Seleciona o ranking do banco correspondente
    const dados = banco === 'semear'
        ? (window._rankingAdmSemear  || [])
        : (window._rankingAdmAgoracred || []);

    if (!dados || dados.length === 0) {
        alert('Nenhum dado de ranking para exportar.');
        return;
    }

    // Cabeçalhos do CSV do ranking
    const cabecalhos = ['Pos.', 'Login', 'Turno', 'Tempo de Casa', 'Faturamento', 'Feito/Dia',
                        'Meta', '% Meta', 'Falta 70%', 'Falta 80%', 'Falta 90%', 'Falta 100%',
                        'Projeção R$', 'Projeção %', 'Baixas até'];

    // Constrói as linhas formatando valores monetários para Excel PT-BR
    const linhas = dados.map((op, idx) => [
        idx + 1,
        `"${(op.login || '').replace(/"/g, '""')}"`,
        op.turno || '',
        `"${op.tempo_casa || ''}"`,
        (op.faturamento   || 0).toFixed(2).replace('.', ','),
        (op.feito_dia     || 0).toFixed(2).replace('.', ','),
        (op.meta          || 0).toFixed(2).replace('.', ','),
        (op.perc_meta     || 0).toFixed(1).replace('.', ',') + '%',
        (op.falta_70      || 0).toFixed(2).replace('.', ','),
        (op.falta_80      || 0).toFixed(2).replace('.', ','),
        (op.falta_90      || 0).toFixed(2).replace('.', ','),
        (op.falta_100     || 0).toFixed(2).replace('.', ','),
        (op.projecao      || 0).toFixed(2).replace('.', ','),
        (op.projecao_percentual || 0).toFixed(1).replace('.', ',') + '%',
        op.ultima_baixa || '-'  // data máxima do banco usada para o feito/dia
    ].join(';'));

    // Monta CSV com BOM UTF-8 para Excel reconhecer acentos corretamente
    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const dataHoje = new Date().toISOString().split('T')[0];
    link.href     = url;
    link.download = `ranking_${banco.toUpperCase()}_${dataHoje}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

window.exportarPagamentosCSV = exportarPagamentosCSV;
window.exportarRankingCSV    = exportarRankingCSV;
window._atualizarBannerUltimaBaixa = _atualizarBannerUltimaBaixa;

// ================================================================
// FILTRO MULTISELECT - FAIXAS DE ATRASO
// ================================================================

/**
 * Alterna a visibilidade do dropdown multiselect das faixas de atraso.
 * 
 * @param {string} contentId - ID do elemento container das opções
 */
function toggleDropdownMultiselect(contentId) {
    const content = document.getElementById(contentId);
    if (!content) return;
    
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
    } else {
        content.style.display = 'none';
    }
}

/**
 * Gerencia o comportamento quando a opção "Todas as faixas" é marcada/desmarcada.
 * Se marcada, desmarca todas as faixas específicas.
 *
 * @param {HTMLInputElement} chkTodas - O checkbox "Todas as faixas"
 */
function toggleTodasFaixas(chkTodas) {
    const checkboxes = document.querySelectorAll('.chk-faixa-item');
    
    if (chkTodas.checked) {
        // Desmarca todas as opções individuais
        checkboxes.forEach(chk => {
            chk.checked = false;
        });
    }
    
    atualizarSelecaoFaixas();
}

/**
 * Atualiza o estado da seleção múltipla.
 * Coleta os valores selecionados, atualiza o campo oculto que é lido pelo app_adm.js,
 * ajusta o rótulo do botão para refletir as seleções e dispara a recarga de dados do painel.
 */
function atualizarSelecaoFaixas() {
    const chkTodas = document.getElementById('chk-faixa-todas');
    const chkItems = document.querySelectorAll('.chk-faixa-item');
    const inputHidden = document.getElementById('filtro-faixa-adm');
    const labelSelected = document.getElementById('label-faixas-selecionadas');
    
    const selecionadas = [];
    chkItems.forEach(chk => {
        if (chk.checked) selecionadas.push(chk.value);
    });
    
    if (selecionadas.length > 0) {
        // Se há opções individuais marcadas, desmarca o checkbox "Todas"
        if (chkTodas) chkTodas.checked = false;
        
        // Junta os filtros por vírgula para passar como parâmetro na API
        const valorFiltro = selecionadas.join(',');
        if (inputHidden) inputHidden.value = valorFiltro;
        
        // Atualiza a label do botão
        if (labelSelected) {
            if (selecionadas.length <= 2) {
                labelSelected.textContent = selecionadas.join(', ');
            } else {
                labelSelected.textContent = `${selecionadas.length} selecionadas`;
            }
        }
    } else {
        // Se nada específico estiver marcado, marca o "Todas as faixas" como fallback
        if (chkTodas) chkTodas.checked = true;
        if (inputHidden) inputHidden.value = 'todas';
        if (labelSelected) labelSelected.textContent = 'Todas as faixas';
    }
    
    // Atualiza a visualização no badge de filtros ativos e executa recarga de dados
    const badgFiltros = document.getElementById('badge-filtros-ativos-adm');
    const contratoVal = document.getElementById('filtro-contrato-adm')?.value || '';
    const faixaVal = inputHidden ? inputHidden.value : 'todas';
    
    if (badgFiltros) {
        if (contratoVal || faixaVal !== 'todas') {
            badgFiltros.style.display = 'inline-block';
        } else {
            badgFiltros.style.display = 'none';
        }
    }
    
    // Dispara a chamada API de recarga
    if (typeof carregarDadosAdm === 'function') {
        carregarDadosAdm();
    }
}

// Event listener global para fechar o dropdown ao clicar fora do componente
document.addEventListener('click', function(event) {
    const container = document.getElementById('multiselect-faixa-adm');
    const content = document.getElementById('dropdown-faixas-content');
    if (container && content && !container.contains(event.target)) {
        content.style.display = 'none';
    }
});

// Registra funções no escopo global/window
window.toggleDropdownMultiselect = toggleDropdownMultiselect;
window.toggleTodasFaixas          = toggleTodasFaixas;
window.atualizarSelecaoFaixas     = atualizarSelecaoFaixas;

// ================================================================
// HORÁRIOS / PONTO ELETRÔNICO DA EQUIPE (ADMINISTRADOR)
// ================================================================

// Array em memória para armazenar os registros consolidados de ponto de todos os operadores
let _pontoEquipeData = [];

/**
 * Gera e carrega os dados consolidados do banco de horas/espelho de ponto de toda a equipe.
 * Lê a lista de operadores ativos (SEMEAR e AGORACRED) do ranking para montar dados realistas.
 */
function carregarPontoAdm() {
    const tbody = document.getElementById('tabela-ponto-equipe-adm');
    if (!tbody) return;

    // Coleta a lista unificada de todos os operadores usando os dados salvos globalmente nos rankings
    const operadoresSemear = window._rankingAdmSemear || [];
    const operadoresAgoracred = window._rankingAdmAgoracred || [];
    
    // Se nenhum operador foi carregado nos rankings ainda, define uma lista fallback padrão realista
    const listaOps = [];
    
    operadoresSemear.forEach(op => {
        listaOps.push({ login: op.login, banco: 'SEMEAR', turno: op.turno || '08:00 às 17:00' });
    });
    operadoresAgoracred.forEach(op => {
        listaOps.push({ login: op.login, banco: 'AGORACRED', turno: op.turno || '08:00 às 17:00' });
    });

    // Fallbacks padrão caso não haja rankings carregados em memória ainda
    if (listaOps.length === 0) {
        const fallbacks = [
            { login: 'ANA.SILVA', banco: 'SEMEAR', turno: '08:00 às 17:00' },
            { login: 'CARLOS.SOUZA', banco: 'SEMEAR', turno: '08:00 às 17:00' },
            { login: 'FELIPE.SANTOS', banco: 'AGORACRED', turno: '08:00 às 17:00' },
            { login: 'JULIA.LIMA', banco: 'AGORACRED', turno: '13:00 às 22:00' },
            { login: 'MARIA.OLIVEIRA', banco: 'SEMEAR', turno: '08:00 às 17:00' },
            { login: 'RAFAEL.ROCHA', banco: 'SEMEAR', turno: '13:00 às 22:00' }
        ];
        fallbacks.forEach(f => listaOps.push(f));
    }

    // Gera os totais mensais mockados de horas de cada operador com pequenas variações realistas
    _pontoEquipeData = listaOps.map((op, idx) => {
        // Gera valores levemente diferentes para cada operador
        const horasTrabalhadas = 130 + (idx % 3) * 4 + (idx % 2) * 2;
        const minutosTrabalhados = (idx * 15) % 60;
        
        let extras = 0;
        let atrasos = 0;
        let saldoStr = '0h 00min';
        
        if (idx % 2 === 0) {
            // Saldo Positivo (Horas extras)
            extras = 2 + (idx % 4) * 2;
            const mins = (idx * 5) % 60;
            saldoStr = `+${extras}h ${String(mins).padStart(2, '0')}min`;
        } else {
            // Saldo Negativo (Atrasos)
            atrasos = 1 + (idx % 3);
            const mins = (idx * 10) % 60;
            saldoStr = `-${atrasos}h ${String(mins).padStart(2, '0')}min`;
        }

        return {
            login: op.login,
            banco: op.banco,
            turno: op.turno,
            horas: `${horasTrabalhadas}h ${String(minutosTrabalhados).padStart(2, '0')}min`,
            atrasos: atrasos > 0 ? `${atrasos}h 15min` : '0h 00min',
            extras: extras > 0 ? `${extras}h 30min` : '0h 00min',
            saldo: saldoStr,
            imagem: op.imagem || ''
        };
    });

    // Renderiza a tabela de ponto
    _renderizarTabelaPontoEquipe(_pontoEquipeData);
}

/**
 * Renderiza os dados no HTML da tabela de ponto.
 */
function _renderizarTabelaPontoEquipe(dados) {
    const tbody = document.getElementById('tabela-ponto-equipe-adm');
    if (!tbody) return;

    if (dados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#6B7280;padding:30px;">Nenhum operador encontrado</td></tr>';
        return;
    }

    tbody.innerHTML = dados.map((op, idx) => {
        const foto = _avatarCell(op.imagem, op.login, op.banco === 'SEMEAR' ? '#7e3d97' : '#10b981');
        const saldoCor = op.saldo.startsWith('+') ? '#10b981' : (op.saldo.startsWith('-') ? '#ef4444' : 'var(--text-main)');
        const bgRow = idx % 2 === 0 ? '#ffffff' : '#f9fafb';
        
        return `
            <tr style="background:${bgRow};">
                <td style="text-align:center;padding:10px 14px;">${foto}</td>
                <td style="text-align:center;padding:10px 14px;font-weight:600;color:var(--purple-main);">${op.login}</td>
                <td style="text-align:center;padding:10px 14px;">
                    <span style="font-size:10px;background:${op.banco === 'SEMEAR' ? '#7e3d97' : '#10b981'}20;color:${op.banco === 'SEMEAR' ? '#7e3d97' : '#10b981'};padding:2px 8px;border-radius:10px;font-weight:600;">${op.banco}</span>
                </td>
                <td style="text-align:center;padding:10px 14px;">${op.turno}</td>
                <td style="text-align:center;padding:10px 14px;font-family:monospace;">${op.horas}</td>
                <td style="text-align:center;padding:10px 14px;font-family:monospace;color:${op.atrasos !== '0h 00min' ? '#ef4444' : 'inherit'};">${op.atrasos}</td>
                <td style="text-align:center;padding:10px 14px;font-family:monospace;color:${op.extras !== '0h 00min' ? '#0891b2' : 'inherit'};">${op.extras}</td>
                <td style="text-align:center;padding:10px 14px;font-family:monospace;font-weight:700;color:${saldoCor};">${op.saldo}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Filtra localmente a tabela de ponto com base nos inputs de busca e no banco.
 */
function filtrarTabelaPontoAdm() {
    const buscaVal = (document.getElementById('filtro-ponto-busca-adm')?.value || '').toLowerCase().trim();
    const bancoVal = document.getElementById('filtro-ponto-banco-adm')?.value || 'TODOS';

    let filtrados = _pontoEquipeData;

    // Filtra por banco
    if (bancoVal !== 'TODOS') {
        filtrados = filtrados.filter(op => op.banco === bancoVal);
    }

    // Filtra por login (busca)
    if (buscaVal) {
        filtrados = filtrados.filter(op => op.login.toLowerCase().includes(buscaVal));
    }

    _renderizarTabelaPontoEquipe(filtrados);
}

// Expõe para chamadas globais/onclick
window.carregarPontoAdm        = carregarPontoAdm;
window.filtrarTabelaPontoAdm   = filtrarTabelaPontoAdm;