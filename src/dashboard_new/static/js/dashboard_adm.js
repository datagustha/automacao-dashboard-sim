/**
 * DASHBOARD ADM - Funções Específicas
 * ====================================
 */

// ================================================================
// RENDERIZAÇÃƒO - DASHBOARD ADM
// ================================================================

function renderizarDashboardAdm(dados) {
    if (!dados) {
        console.warn('âš ï¸ Dados não fornecidos para renderizarDashboardAdm');
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
    const setaSemear = variacaoSemear >= 0 ? '<i class="fas fa-arrow-up" style="margin-right:2px;"></i>' : '<i class="fas fa-arrow-down" style="margin-right:2px;"></i>';
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
    const setaAgoracred = variacaoAgoracred >= 0 ? '<i class="fas fa-arrow-up" style="margin-right:2px;"></i>' : '<i class="fas fa-arrow-down" style="margin-right:2px;"></i>';
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

    // --- CÃLCULO E EXIBIÇÃƒO DE ÃšLTIMO RECEBIMENTO POR BANCO ---
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
    const setaOps = variacaoOps >= 0 ? '<i class="fas fa-arrow-up" style="margin-right:2px;"></i>' : '<i class="fas fa-arrow-down" style="margin-right:2px;"></i>';
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
    const setaTk = variacaoTk >= 0 ? '<i class="fas fa-arrow-up" style="margin-right:2px;"></i>' : '<i class="fas fa-arrow-down" style="margin-right:2px;"></i>';
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
    // GRÃFICOS
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
    _atualizarBannerUltimaBaixa('semear', semear.ultima_baixa, semear.operadores);
    _atualizarBannerUltimaBaixa('agoracred', agoracred.ultima_baixa, agoracred.operadores);

    // ============================================================
    // TABELA - Faixas SEMEAR (COM FOTOS)
    // ============================================================
    renderizarFaixasSemear(semear.faixas || []);
    // Guarda dados das faixas globalmente para exportação CSV
    window._faixasAdmSemear = semear.faixas || [];

    // ============================================================
    // TABELA - Evolução Operadores
    // ============================================================
    renderizarEvolucaoOperadores(dados.evolucao_operadores || []);
    // Guarda dados da evolução de operadores para exportação CSV
    window._evolucaoOperadoresAdm = dados.evolucao_operadores || [];

    // ============================================================
    // RELATÓRIO DIRETORIA: FAIXA DE ATRASO VS MÊS (SEMEAR)
    // ============================================================
    if (typeof renderizarMatrizFaixasAdm === 'function') {
        renderizarMatrizFaixasAdm(semear.matriz_faixas_mes || null);
    }

    // ============================================================
    // VISÃO TRIMESTRAL POR DIA ÚTIL — SEMEAR / AGORACRED
    // ============================================================
    if (typeof renderizarTrimestreDUAdm === 'function') {
        renderizarTrimestreDUAdm('semear', semear.trimestre_du || null);
        renderizarTrimestreDUAdm('agoracred', agoracred.trimestre_du || null);
    }
    // Guarda dados trimestrais globalmente para exportação CSV
    window._trimestreDUSemear   = semear.trimestre_du   || null;
    window._trimestreDUAgoracred = agoracred.trimestre_du || null;
    // Guarda dados do resultado mês a mês
    window._resultadoMesSemear   = semear.resultado_mes_a_mes   || [];
    window._resultadoMesAgoracred = agoracred.resultado_mes_a_mes || [];
    // Guarda dados da evolução diária para exportação
    window._evolucaoDiariaAdmSemear   = semear.evolucao   || [];
    window._evolucaoDiariaAdmAgoracred = agoracred.evolucao || [];

    // ============================================================
    // ALERTAS DE OPERADORES INATIVOS (> 2 DIAS SEM RECEBIMENTO)
    // ============================================================
    if (typeof exibirAlertasInativosAdm === 'function') {
        const rankingCompleto = [...(semear.operadores || []), ...(agoracred.operadores || [])];
        exibirAlertasInativosAdm(rankingCompleto);
    }
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
// RENDERIZAÇÃO - VISÃO TRIMESTRAL POR DIA ÚTIL (ADM)
// ================================================================

function renderizarTrimestreDUAdm(banco, dados) {
    const idMap = {
        semear: 'tabela-trimestre-du-semear',
        agoracred: 'tabela-trimestre-du-agoracred'
    };
    const corMap = {
        semear: '#7E3E9A',
        agoracred: '#047857'
    };
    const bgTotalMap = {
        semear: '#f3e8ff',
        agoracred: '#d1fae5'
    };

    const tbodyId = idMap[banco] || 'tabela-trimestre-du-semear';
    const cor = corMap[banco] || '#7E3E9A';
    const bgTotal = bgTotalMap[banco] || '#f3e8ff';

    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;

    if (!dados || !dados.linhas || dados.linhas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#95a5a6;padding:20px;">Sem dados trimestrais disponíveis.</td></tr>`;
        return;
    }

    const colunas = dados.colunas || [];
    const prefixo = banco;
    ['m0', 'm1', 'm2'].forEach((suf, i) => {
        const el = document.getElementById(`th-trimestre-${prefixo}-${suf}`);
        if (el && colunas[i]) el.textContent = colunas[i];
    });

    const linhas = dados.linhas || [];
    let html = '';

    linhas.forEach(linha => {
        const vAtual = linha.v_atual || 0;
        const vM1 = linha.v_m1 || 0;
        const vM2 = linha.v_m2 || 0;
        const corAtual = vAtual > vM1 ? '#16a34a' : (vAtual < vM1 ? '#dc2626' : '#374151');
        const bgAtual  = vAtual > vM1 ? '#dcfce7' : (vAtual < vM1 ? '#fee2e2' : 'transparent');

        html += `
            <tr style="border-bottom:1px solid #f0f0f0;">
                <td style="padding:8px 14px;text-align:center;font-weight:700;color:${cor};">${linha.dia_util || '-'}</td>
                <td style="padding:8px 14px;text-align:center;color:#6b7280;font-size:12px;">${linha.data_atual || '-'}</td>
                <td style="padding:8px 14px;text-align:center;font-weight:700;color:${corAtual};background:${bgAtual};border-radius:6px;">${formatarMoeda(vAtual)}</td>
                <td style="padding:8px 14px;text-align:center;color:#374151;">${vM1 > 0 ? formatarMoeda(vM1) : '<span style="color:#9ca3af;">—</span>'}</td>
                <td style="padding:8px 14px;text-align:center;color:#374151;">${vM2 > 0 ? formatarMoeda(vM2) : '<span style="color:#9ca3af;">—</span>'}</td>
            </tr>
        `;
    });

    if (dados.totais) {
        const t = dados.totais;
        const totAtual = t.total_atual !== undefined ? t.total_atual : (t.v_atual || 0);
        const totM1 = t.total_m1 !== undefined ? t.total_m1 : (t.v_m1 || 0);
        const totM2 = t.total_m2 !== undefined ? t.total_m2 : (t.v_m2 || 0);

        html += `
            <tr style="background:${bgTotal};font-weight:800;border-top:2px solid ${cor};">
                <td colspan="2" style="padding:10px 14px;text-align:center;color:${cor};">TOTAL DO PERÍODO</td>
                <td style="padding:10px 14px;text-align:center;color:${cor};">${formatarMoeda(totAtual)}</td>
                <td style="padding:10px 14px;text-align:center;">${totM1 > 0 ? formatarMoeda(totM1) : '—'}</td>
                <td style="padding:10px 14px;text-align:center;">${totM2 > 0 ? formatarMoeda(totM2) : '—'}</td>
            </tr>
        `;
    }

    tbody.innerHTML = html;
}


// ================================================================
// RENDERIZAÇÃO - RELATÓRIO FAIXA DE ATRASO VS MÊS (ADM)
// ================================================================

function renderizarMatrizFaixasAdm(dados) {
    const tbody = document.getElementById('tabela-faixa-vs-mes-adm');
    if (!tbody) return;

    // Armazena para exportação CSV
    window._matrizFaixasAdm = dados;

    if (!dados || !dados.linhas || dados.linhas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="14" style="text-align:center;color:#95a5a6;padding:20px;">Sem dados disponíveis para o relatório de faixas.</td></tr>';
        return;
    }

    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    const mesAtualIdx = new Date().getMonth(); // 0-indexed
    const linhas = dados.linhas || [];
    let html = '';

    linhas.forEach((linha, idx) => {
        const bgRow = idx % 2 === 0 ? '#ffffff' : '#faf5ff';
        let rowHtml = `<tr style="background:${bgRow};border-bottom:1px solid #e5e7eb;">
            <td style="padding:9px 14px;font-weight:700;color:#7E3E9A;border-right:2px solid #e5e7eb;white-space:nowrap;">${linha.faixa || '-'}</td>`;

        meses.forEach((mes, mIdx) => {
            const val     = linha[mes]    || 0;
            const valPrev = mIdx > 0 ? (linha[meses[mIdx - 1]] || 0) : null;
            const cor = val > 0 ? '#612d75' : '#9ca3af';

            // Delta vs mês anterior (só para mês atual e até o mês anterior ao atual)
            let deltaHtml = '';
            if (mIdx <= mesAtualIdx && valPrev !== null && (val > 0 || valPrev > 0)) {
                const diff = val - valPrev;
                if (diff > 0) {
                    deltaHtml = `<div style="font-size:9px;color:#16a34a;font-weight:700;margin-top:1px;">▲ +${formatarMoeda(diff)}</div>`;
                } else if (diff < 0) {
                    deltaHtml = `<div style="font-size:9px;color:#dc2626;font-weight:700;margin-top:1px;">▼ ${formatarMoeda(Math.abs(diff))}</div>`;
                } else if (val > 0) {
                    deltaHtml = `<div style="font-size:9px;color:#6b7280;margin-top:1px;">— igual</div>`;
                }
            }

            rowHtml += `<td style="padding:7px 12px;text-align:center;color:${cor};font-weight:${val > 0 ? '600' : '400'};">${val > 0 ? formatarMoeda(val) : '—'}${deltaHtml}</td>`;
        });

        const totalAno = linha.total_ano || 0;
        rowHtml += `<td style="padding:9px 12px;text-align:center;font-weight:800;color:#612d75;background:#f3e8ff;">${formatarMoeda(totalAno)}</td></tr>`;
        html += rowHtml;
    });

    if (dados.totais) {
        const t = dados.totais;
        let totalRow = `<tr style="background:#7E3E9A;color:#ffffff !important;font-weight:800;">
            <td style="padding:10px 14px;border-right:2px solid #612d75;color:#ffffff !important;">TOTAL GERAL</td>`;
        meses.forEach(mes => {
            const val = t[mes] || 0;
            totalRow += `<td style="padding:10px 12px;text-align:center;color:#ffffff !important;font-weight:800;">${val > 0 ? formatarMoeda(val) : '—'}</td>`;
        });
        totalRow += `<td style="padding:10px 12px;text-align:center;background:#612d75;color:#ffffff !important;font-weight:800;">${formatarMoeda(t.total_ano || 0)}</td></tr>`;
        html += totalRow;
    }

    tbody.innerHTML = html;
}


// ================================================================
// ALERTA DE OPERADORES INATIVOS — ADM
// Exibe banner amarelo com badges de quem está > 2 DU sem pgto.
// Recebe lista de operadores com: { login, dias_sem_pgto, banco }
// ================================================================

function exibirAlertasInativosAdm(operadores) {
    const banner = document.getElementById('banner-alertas-inativos-adm');
    const lista = document.getElementById('lista-alertas-inativos-adm');
    if (!banner || !lista) return;

    const inativos = (operadores || []).filter(op => (op.dias_sem_pgto || 0) >= 2 || op.alerta_sem_pgto);

    if (inativos.length === 0) {
        banner.style.display = 'none';
        return;
    }

    banner.style.display = 'block';

    lista.innerHTML = inativos.map(op => {
        const dias = op.dias_sem_pgto || 0;
        const banco = op.banco || 'SEMEAR';
        const corBanco = banco === 'AGORACRED' ? '#10B981' : '#7E3E9A';
        const fotoHtml = _avatarCell(op.imagem, op.login || op.operador, corBanco);
        const ultData = op.ultima_data_op || op.ultima_baixa || '-';
        const ultVal = op.ultimo_valor_pgto ? formatarMoeda(op.ultimo_valor_pgto) : '';

        return `
            <div style="display:inline-flex;align-items:center;gap:10px;background:#ffffff;border-radius:10px;padding:8px 14px;border-left:4px solid ${corBanco};box-shadow:0 2px 6px rgba(0,0,0,0.06);margin-right:8px;margin-bottom:8px;">
                <div style="flex-shrink:0;">${fotoHtml}</div>
                <div style="display:flex;flex-direction:column;gap:2px;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-weight:700;color:#1f2937;font-size:13px;">${op.login || op.operador}</span>
                        <span style="background:${corBanco};color:white;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:700;">${banco}</span>
                    </div>
                    <div style="font-size:11px;color:#6b7280;display:flex;align-items:center;gap:8px;">
                        <span><i class="fas fa-calendar-day" style="color:${corBanco};"></i> Último pgto: <strong>${ultData}</strong> ${ultVal ? `(${ultVal})` : ''}</span>
                        <span style="background:#fee2e2;color:#991b1b;border-radius:12px;padding:2px 8px;font-weight:700;font-size:11px;display:inline-flex;align-items:center;gap:4px;">
                            <i class="fas fa-triangle-exclamation" style="color:#d97706;"></i> ${dias} DU sem pgto
                        </span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}
window.exibirAlertasInativosAdm = exibirAlertasInativosAdm;


// ================================================================
// RENDERIZAÇÃO - EVOLUÇÃO DIÁRIA
// ================================================================


function renderizarEvolucaoDiaria(semear, agoracred) {
    const tbody = document.getElementById('tabela-evolucao-diaria-adm');
    if (!tbody) return;

    // Mapeia por data para cruzar os dois bancos
    const mapSemear = {};
    semear.forEach(d => { mapSemear[d.data || d.data_formatada] = d; });

    const mapAgoracred = {};
    agoracred.forEach(d => { mapAgoracred[d.data || d.data_formatada] = d; });

    // Usa datas do semear como referência principal (já preenchido com seg-sex)
    const todasDatas = new Set([
        ...semear.map(d => d.data || ''),
        ...agoracred.map(d => d.data || '')
    ]);
    const diasArray = Array.from(todasDatas).filter(Boolean).sort();

    if (diasArray.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
        return;
    }

    // Dias da semana para formatação local (fallback)
    const diasSemAbrev = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sab'];

    let html = '';
    let totalSemear = 0;
    let totalAgoracred = 0;

    diasArray.forEach(data => {
        const s = mapSemear[data] || { total: 0, realizado: 0 };
        const a = mapAgoracred[data] || { total: 0, realizado: 0 };
        const vS = s.total || s.realizado || 0;
        const vA = a.total || a.realizado || 0;
        const total = vS + vA;

        totalSemear += vS;
        totalAgoracred += vA;

        // Usa data_formatada do backend se disponível (ex: "24 - sex"),
        // senão calcula localmente a partir da string YYYY-MM-DD
        let diaExib = s.data_formatada || a.data_formatada || null;
        if (!diaExib && data && data.includes('-')) {
            const partes = data.split('-');
            const diaNum = parseInt(partes[2], 10);
            const dataObj = new Date(parseInt(partes[0]), parseInt(partes[1]) - 1, diaNum);
            const nomeDia = diasSemAbrev[dataObj.getDay()] || '';
            diaExib = `${diaNum} - ${nomeDia}`;
        }

        html += `
            <tr>
                <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;font-weight:600;">${diaExib || data}</td>
                <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;">${formatarMoeda(vS)}</td>
                <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;">${formatarMoeda(vA)}</td>
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
        const corMetaText = percMeta >= 100 ? '#10B981' : '#064e3b';

        const progressoHtml = `
            <div class="table-progress-container">
                <div class="table-progress-bar">
                    <div class="table-progress-fill" style="width: ${Math.min(percMeta, 100)}%; background: #10B981;"></div>
                </div>
                <span class="table-progress-text" style="color: ${corMetaText}; font-weight: 700;">${percMeta.toFixed(1)}%</span>
            </div>
        `;

        const projecaoProgressoHtml = `
            <div class="table-progress-container">
                <div class="table-progress-bar">
                    <div class="table-progress-fill" style="width: ${Math.min(projecaoPct, 100)}%; background: #10B981;"></div>
                </div>
                <span class="table-progress-text" style="color: #064e3b; font-weight: 700;">${projecaoPct.toFixed(1)}%</span>
            </div>
        `;


        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;font-weight:600;font-size:14px;">${medalha}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-3 sticky-col-name" style="text-align:center;padding:8px 10px;font-weight:700;color:#064e3b;">${op.login || '-'}</td>

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
                <div class="table-progress-fill agoracred-green" style="width: ${Math.min(totalPerc, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: #047857;">${totalPerc.toFixed(1)}%</span>
        </div>
    `;

    const totalProjecaoProgressoHtml = `
        <div class="table-progress-container">
            <div class="table-progress-bar">
                <div class="table-progress-fill agoracred-green" style="width: ${Math.min(totalProjecaoPct, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: #374151;">${totalProjecaoPct.toFixed(1)}%</span>
        </div>
    `;

    const tr = `
        <tr style="background:#d1fae5;font-weight:bold;">
            <td class="sticky-col-1" style="text-align:center;padding:10px;color:#047857;" colspan="2"><strong>TOTAL</strong></td>
            <td class="sticky-col-3" style="text-align:center;padding:10px;color:#047857;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#047857;">${formatarMoeda(totalFat)}</td>
            <td style="text-align:center;padding:10px;"></td>
            <td style="text-align:center;padding:10px;color:#047857;">${formatarMoeda(totalMeta)}</td>
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

    window._faixasAdmSemear = faixas;

    if (!faixas || faixas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="14" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
        return;
    }

    const modo = window._faixasModoVisualizacao || 'valor';

    // Todas as faixas em ordem (operadores aparecem UMA vez com TODAS as colunas)
    const faixasBaixo = ['Fase 10 a 30','Fase 31 a 60','Fase 61 a 90','Fase 91 a 120','Fase 121 a 180','Fase 181 a 240','Fase 241 a 360'];
    const faixasAlto  = ['Fase 361 a 720','Fase 721 a 1080','Fase 1081 a 1440','Fase 1441 a 1800','> 1800'];
    const colunasFases = [...faixasBaixo, ...faixasAlto];

    // --- Linhas de operadores (cada um aparece UMA vez com todas as colunas) ---
    let html = faixas.map((op, idx) => {
        const bg = idx % 2 === 0 ? '#ffffff' : '#faf5ff';
        const foto = _avatarCell(op.imagem, op.operador, '#7e3d97');
        let row = `<tr style="background:${bg};">
            <td class="sticky-col-1" style="text-align:center;padding:8px 10px;">${foto}</td>
            <td class="sticky-col-2 sticky-col-name" style="text-align:center;padding:8px 10px;font-weight:600;color:var(--purple-main);">${op.operador || '-'}</td>`;
        colunasFases.forEach(fase => {
            const chave = modo === 'qtd' ? `${fase}_qtd` : fase;
            const valor = op[chave] || 0;
            const cor = valor > 0 ? 'var(--text-main)' : '#9ca3af';
            const valorFmt = modo === 'qtd' ? parseInt(valor) : formatarMoeda(valor);
            row += `<td class="faixa-atraso-col" style="color:${cor};text-align:center;">${valorFmt}</td>`;
        });
        row += '</tr>';
        return row;
    }).join('');

    // --- Subtotal ≤ 360 dias (mostra só colunas baixo atraso, resto em branco) ---
    const totaisBaixo = {};
    faixasBaixo.forEach(fase => {
        const chave = modo === 'qtd' ? `${fase}_qtd` : fase;
        totaisBaixo[fase] = faixas.reduce((s, op) => s + (op[chave] || 0), 0);
    });
    html += `<tr style="background:#bbf7d0;">
        <td class="sticky-col-1" style="text-align:center;padding:8px;"></td>
        <td class="sticky-col-2" style="padding:8px 10px;font-weight:800;font-size:11px;color:#065f46;white-space:nowrap;">✅ SUBTOTAL ≤ 360 dias</td>`;
    colunasFases.forEach(fase => {
        if (faixasBaixo.includes(fase)) {
            const v = totaisBaixo[fase];
            const vFmt = modo === 'qtd' ? parseInt(v) : formatarMoeda(v);
            html += `<td class="faixa-atraso-col" style="font-weight:700;color:#065f46;text-align:center;background:#dcfce7;">${vFmt}</td>`;
        } else {
            html += `<td class="faixa-atraso-col" style="background:#f0fdf4;"></td>`;
        }
    });
    html += '</tr>';

    // --- Subtotal > 360 dias (mostra só colunas alto atraso, resto em branco) ---
    const totaisAlto = {};
    faixasAlto.forEach(fase => {
        const chave = modo === 'qtd' ? `${fase}_qtd` : fase;
        totaisAlto[fase] = faixas.reduce((s, op) => s + (op[chave] || 0), 0);
    });
    html += `<tr style="background:#fecaca;">
        <td class="sticky-col-1" style="text-align:center;padding:8px;"></td>
        <td class="sticky-col-2" style="padding:8px 10px;font-weight:800;font-size:11px;color:#991b1b;white-space:nowrap;">⚠️ SUBTOTAL > 360 dias</td>`;
    colunasFases.forEach(fase => {
        if (faixasAlto.includes(fase)) {
            const v = totaisAlto[fase];
            const vFmt = modo === 'qtd' ? parseInt(v) : formatarMoeda(v);
            html += `<td class="faixa-atraso-col" style="font-weight:700;color:#991b1b;text-align:center;background:#fee2e2;">${vFmt}</td>`;
        } else {
            html += `<td class="faixa-atraso-col" style="background:#fff7f7;"></td>`;
        }
    });
    html += '</tr>';

    // --- Total Geral ---
    const totaisGeral = {};
    colunasFases.forEach(fase => {
        const chave = modo === 'qtd' ? `${fase}_qtd` : fase;
        totaisGeral[fase] = faixas.reduce((s, op) => s + (op[chave] || 0), 0);
    });
    html += `<tr style="background:#7E3E9A;color:#ffffff;font-weight:800;">
        <td class="sticky-col-1" style="text-align:center;padding:10px;"></td>
        <td class="sticky-col-2" style="padding:10px 14px;color:#ffffff;font-weight:800;">TOTAL GERAL</td>`;
    colunasFases.forEach(fase => {
        const val = totaisGeral[fase];
        const valFmt = modo === 'qtd' ? parseInt(val) : formatarMoeda(val);
        html += `<td class="faixa-atraso-col" style="color:#ffffff;font-weight:800;text-align:center;">${valFmt}</td>`;
    });
    html += '</tr>';

    tbody.innerHTML = html;

    // Atualiza o banner de alto vs baixo atraso
    if (typeof atualizarBannerAltoBaixoAtraso === 'function') {
        atualizarBannerAltoBaixoAtraso(faixas);
    }
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
    const atividade = document.getElementById('filtro-atividade-adm')?.value || 'ATIVO';

    const dataInicio = document.getElementById('filtro-pag-inicio-adm')?.value || '';
    const dataFim = document.getElementById('filtro-pag-fim-adm')?.value || '';
    const duInicio = document.getElementById('filtro-du-inicio-adm')?.value || '';
    const duFim = document.getElementById('filtro-du-fim-adm')?.value || '';

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
        if (duInicio) url += `&du_inicio=${duInicio}`;
        if (duFim) url += `&du_fim=${duFim}`;

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

            // Resumo rápido — calculado com base nos dados brutos (atualiza ao filtrar)
            _atualizarResumoPagAdm(_pagamentosAdmData);

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

function _atualizarResumoPagAdm(dados) {
    const resumoEl = document.getElementById('pag-adm-resumo');
    if (!resumoEl) return;
    const totalFat = dados.reduce((s, p) => s + (p.valorTotal || 0), 0);
    const qtd = dados.length;
    const ticket = qtd > 0 ? totalFat / qtd : 0;
    resumoEl.innerHTML = `
        <div style="background:linear-gradient(135deg,#7e3d97,#a855f7);color:white;border-radius:12px;padding:12px 20px;flex:1;">
            <div style="font-size:11px;opacity:0.8;text-transform:uppercase;margin-bottom:4px;">Total Faturamento</div>
            <div style="font-size:22px;font-weight:700;">${formatarMoeda(totalFat)}</div>
        </div>
        <div style="background:linear-gradient(135deg,#0891b2,#22d3ee);color:white;border-radius:12px;padding:12px 20px;flex:1;">
            <div style="font-size:11px;opacity:0.8;text-transform:uppercase;margin-bottom:4px;">Qtd. Pagamentos</div>
            <div style="font-size:22px;font-weight:700;">${qtd}</div>
        </div>
        <div style="background:linear-gradient(135deg,#10B981,#34d399);color:white;border-radius:12px;padding:12px 20px;flex:1;">
            <div style="font-size:11px;opacity:0.8;text-transform:uppercase;margin-bottom:4px;">Ticket Médio</div>
            <div style="font-size:22px;font-weight:700;">${formatarMoeda(ticket)}</div>
        </div>
    `;
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

    // Atualiza o resumo com os dados filtrados
    _atualizarResumoPagAdm(filtrados);

    if (totalEl) totalEl.textContent = `${filtrados.length} registros`;

    const total = filtrados.length;
    const totalPages = Math.max(1, Math.ceil(total / _pagAdmPerPage));
    _pagAdmPage = Math.min(_pagAdmPage, totalPages);
    const inicio = (_pagAdmPage - 1) * _pagAdmPerPage;
    const pagina = filtrados.slice(inicio, inicio + _pagAdmPerPage);

    if (pagina.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#6B7280;padding:30px;">Nenhum pagamento encontrado com os filtros aplicados.</td></tr>';
    } else {
        tbody.innerHTML = pagina.map(p => {
            const bancoCor = (p.banco || '') === 'SEMEAR' ? '#7E3E9A' : '#10B981';
            const isAgoracred = p.banco === 'AGORACRED';
            const atrasoVal = isAgoracred ? '—' : (p.atraso !== null && p.atraso !== undefined ? p.atraso + 'd' : '-');
            const maiorAtrasoVal = isAgoracred ? '—' : (p.maiorAtraso !== null && p.maiorAtraso !== undefined ? p.maiorAtraso + 'd' : '-');
            const maiorAtrasoColor = !isAgoracred && p.maiorAtraso >= 360 ? '#dc2626' : (!isAgoracred && p.maiorAtraso >= 90 ? '#d97706' : 'var(--text-main)');
            return `
                <tr>
                    <td style="padding:8px 10px;text-align:center;font-size:12px;white-space:nowrap;">${formatarData(p.dtPgto) || '-'}</td>
                    <td style="padding:8px 10px;text-align:center;font-weight:600;">${p.contrato || '-'}</td>
                    <td style="padding:8px 10px;text-align:left;">${p.cliente || '-'}</td>
                    <td style="padding:8px 10px;text-align:center;">
                        <span style="background:${bancoCor};color:white;padding:1px 8px;border-radius:10px;font-size:10px;font-weight:600;">${p.banco || '-'}</span>
                    </td>
                    <td style="padding:8px 10px;text-align:center;font-size:12px;">${p.operador || p.login || '-'}</td>
                    <td style="padding:8px 10px;text-align:center;font-size:11px;color:var(--text-muted);">${isAgoracred ? '—' : (p.faseAtraso || '-')}</td>
                    <td style="padding:8px 10px;text-align:center;font-size:12px;color:var(--text-muted);">${atrasoVal}</td>
                    <td style="padding:8px 10px;text-align:center;font-size:12px;font-weight:600;color:${maiorAtrasoColor};">${maiorAtrasoVal}</td>
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
        html += `<button onclick="_pagAdmIr(${_pagAdmPage-1})" ${prev?'':'disabled'} style="padding:4px 10px;border-radius:6px;border:1px solid #d1d5db;cursor:${prev?'pointer':'not-allowed'};background:${prev?'white':'#f3f4f6'};">&laquo;</button>`;
        const start = Math.max(1, _pagAdmPage - 2);
        const end = Math.min(totalPages, _pagAdmPage + 2);
        for (let i = start; i <= end; i++) {
            html += `<button onclick="_pagAdmIr(${i})" style="padding:4px 10px;border-radius:6px;border:1px solid ${i===_pagAdmPage?'var(--purple-main)':'#d1d5db'};background:${i===_pagAdmPage?'var(--purple-main)':'white'};color:${i===_pagAdmPage?'white':'inherit'};font-weight:${i===_pagAdmPage?'700':'400'};cursor:pointer;">${i}</button>`;
        }
        html += `<button onclick="_pagAdmIr(${_pagAdmPage+1})" ${next?'':'disabled'} style="padding:4px 10px;border-radius:6px;border:1px solid #d1d5db;cursor:${next?'pointer':'not-allowed'};background:${next?'white':'#f3f4f6'};">&raquo;</button>`;
        html += `<span style="font-size:12px;color:var(--text-muted);margin-left:8px;">${inicio+1} a ${Math.min(inicio+_pagAdmPerPage,total)} de ${total}</span>`;
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
window._atualizarResumoPagAdm = _atualizarResumoPagAdm;


// ================================================================
// RENDERIZAÇÃO - EVOLUÇÃO OPERADORES
// ================================================================

function renderizarEvolucaoOperadores(operadores) {
    const tbody = document.getElementById('tabela-evolucao-operadores-adm');
    const resumo = document.getElementById('resumo-evolucao-adm');

    if (!tbody) return;

    if (!operadores || operadores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="13" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado disponível</td></tr>';
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

    operadores.sort((a, b) => {
        const projA = a.projecao_percentual !== undefined ? a.projecao_percentual : (a.meta > 0 ? (a.projecao / a.meta) * 100 : 0);
        const projB = b.projecao_percentual !== undefined ? b.projecao_percentual : (b.meta > 0 ? (b.projecao / b.meta) * 100 : 0);
        return projB - projA;
    });

    tbody.innerHTML = operadores.map(op => {
        // ── Variação: ÚNICO lugar com vermelho/verde ──
        const varPct   = op.variacao_percentual || 0;
        const corVar   = varPct >= 0 ? 'var(--emerald)' : '#e74c3c';
        const setaVar  = varPct >= 0 ? '▲' : '▼';
        const sinalVar = varPct >= 0 ? '+' : '';

        // ── Banco: cor e label ──
        const bancoCor   = op.banco === 'SEMEAR' ? '#7E3E9A' : '#10B981';
        const bancoLabel = op.banco === 'SEMEAR' ? 'SEMEAR' : 'AGORACRED';
        const barraClasse = op.banco === 'SEMEAR' ? 'purple' : 'agoracred-green';
        const foto = _avatarCell(op.imagem, op.operador, bancoCor);

        // ── % Meta atual — barra cor do banco ──
        const percAtual = op.perc_meta_atual || 0;
        const percAnt   = op.perc_meta_anterior || 0;
        const barraAtual = `
            <div class="table-progress-container" style="min-width:96px;">
                <div class="table-progress-bar">
                    <div class="table-progress-fill ${barraClasse}" style="width:${Math.min(percAtual,100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color:${percAtual>=100?bancoCor:'#374151'};">${percAtual.toFixed(1)}%</span>
            </div>`;
        const barraAnt = `
            <div class="table-progress-container" style="min-width:96px;">
                <div class="table-progress-bar">
                    <div class="table-progress-fill ${barraClasse}" style="width:${Math.min(percAnt,100)}%;opacity:0.45;"></div>
                </div>
                <span class="table-progress-text" style="color:#9ca3af;">${percAnt.toFixed(1)}%</span>
            </div>`;

        // ── Var pp — discreto ──
        const varPP  = op.variacao_meta_pp || 0;
        const corPP  = varPP >= 0 ? 'var(--emerald)' : '#e74c3c';
        const setaPP = varPP >= 0 ? '▲' : '▼';

        // ── Projeção — barra cor do banco, texto neutro ──
        const projR$  = op.projecao || 0;
        const projPct = op.projecao_percentual != null ? op.projecao_percentual : (op.meta > 0 ? (projR$ / op.meta) * 100 : 0);
        const barraProj = `
            <div class="table-progress-container" style="min-width:96px;">
                <div class="table-progress-bar">
                    <div class="table-progress-fill ${barraClasse}" style="width:${Math.min(projPct,100)}%;"></div>
                </div>
                <span class="table-progress-text" style="color:#374151;">${projPct.toFixed(1)}%</span>
            </div>`;

        return `
            <tr>
                <td class="sticky-col-1" style="text-align:center;padding:8px 10px;">${foto}</td>
                <td class="sticky-col-2" style="text-align:center;padding:8px 6px;">
                    <span style="background:${bancoCor};color:white;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;">${bancoLabel}</span>
                </td>
                <td class="sticky-col-3 sticky-col-name" style="text-align:left;padding:8px 10px;font-weight:600;color:#1f2937;">${op.operador || '-'}</td>
                <td style="text-align:right;padding:8px 14px;font-weight:600;color:#1f2937;">${formatarMoeda(op.fat_atual || 0)}</td>
                <td style="text-align:right;padding:8px 14px;color:#6b7280;">${formatarMoeda(op.fat_anterior || 0)}</td>
                <td style="text-align:right;padding:8px 14px;color:${corVar};font-weight:700;">${formatarMoeda(op.variacao || 0)}</td>
                <td style="text-align:center;padding:8px 10px;color:${corVar};font-weight:700;">${setaVar} ${sinalVar}${varPct.toFixed(1)}%</td>
                <td style="text-align:center;padding:8px 8px;">${barraAtual}</td>
                <td style="text-align:center;padding:8px 8px;">${barraAnt}</td>
                <td style="text-align:center;padding:8px 10px;font-weight:600;color:${corPP};">${setaPP} ${varPP>=0?'+':''}${varPP.toFixed(1)} pp</td>
                <td style="text-align:right;padding:8px 14px;color:#374151;font-weight:600;">${formatarMoeda(projR$)}</td>
                <td style="text-align:center;padding:8px 8px;">${barraProj}</td>
            </tr>`;
    }).join('');

    // ── Linha de total — neutra ──
    const totAtual = operadores.reduce((s,op)=>s+(op.fat_atual||0),0);
    const totAnt   = operadores.reduce((s,op)=>s+(op.fat_anterior||0),0);
    const totVar   = totAnt>0?((totAtual-totAnt)/totAnt)*100:0;
    const totDif   = totAtual-totAnt;
    const corTot   = totVar>=0?'var(--emerald)':'#e74c3c';
    const setaTot  = totVar>=0?'▲':'▼';
    const totProj  = operadores.reduce((s,op)=>s+(op.projecao||0),0);
    const totMeta  = operadores.reduce((s,op)=>s+(op.meta||0),0);
    const totPct   = totMeta>0?(totProj/totMeta)*100:0;
    const barraTot = `
        <div class="table-progress-container" style="min-width:96px;">
            <div class="table-progress-bar">
                <div class="table-progress-fill purple" style="width:${Math.min(totPct,100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color:#374151;">${totPct.toFixed(1)}%</span>
        </div>`;

    tbody.innerHTML += `
        <tr style="background:#f8f9fa;font-weight:700;border-top:2px solid #e5e7eb;">
            <td class="sticky-col-1" style="padding:10px;"></td>
            <td class="sticky-col-2" style="padding:10px;"></td>
            <td class="sticky-col-3" style="padding:10px;text-align:left;color:#374151;">TOTAL</td>
            <td style="text-align:right;padding:10px;color:#374151;">${formatarMoeda(totAtual)}</td>
            <td style="text-align:right;padding:10px;color:#6b7280;">${formatarMoeda(totAnt)}</td>
            <td style="text-align:right;padding:10px;color:${corTot};">${formatarMoeda(totDif)}</td>
            <td style="text-align:center;padding:10px;color:${corTot};">${setaTot} ${totVar>=0?'+':''}${totVar.toFixed(1)}%</td>
            <td style="padding:10px;"></td><td style="padding:10px;"></td><td style="padding:10px;"></td>
            <td style="text-align:right;padding:10px;color:#374151;">${formatarMoeda(totProj)}</td>
            <td style="padding:10px;">${barraTot}</td>
        </tr>`;
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
function _atualizarBannerUltimaBaixa(banco, ultimaBaixa, operadores) {
    // IDs dos elementos HTML criados no dashboard_adm.html
    const bannerEl = document.getElementById(`banner-ultima-baixa-${banco}`);
    const textoEl  = document.getElementById(`txt-ultima-baixa-${banco}`);
    if (!bannerEl || !textoEl) return;

    if (ultimaBaixa) {
        // Exibe o banner com a data máxima do banco e o Dia Útil correspondente
        const duCalculado = typeof calcularDUdaData === 'function' ? calcularDUdaData(ultimaBaixa) : '';
        const tagDu = duCalculado ? ` <span style="background:rgba(255,255,255,0.7);padding:2px 8px;border-radius:6px;font-size:12px;font-weight:700;margin-left:6px;border:1px solid currentColor;">${duCalculado}</span>` : '';
        
        let extrasHtml = '';
        if (operadores && operadores.length > 0) {
            const op = operadores[0];
            const dTrabalhados = op.dias_trabalhados || 0;
            const dTotal = op.total_dias_uteis || 0;
            const dRestantes = Math.max(0, dTotal - dTrabalhados);
            
            const isAgoracred = banco === 'agoracred';
            const iconColor = isAgoracred ? 'color:#10b981;opacity:0.8;' : 'color:var(--purple-main);opacity:0.8;';
            
            extrasHtml = `
            <div style="margin-top:6px;font-size:12.5px;font-weight:600;display:flex;gap:12px;color:var(--text-main);align-items:center;flex-wrap:wrap;">
                <span><i class="fas fa-calendar-check" style="margin-right:4px;${iconColor}"></i>Dias úteis trabalhados: ${dTrabalhados}</span>
                <span style="color:#cbd5e1;">|</span>
                <span><i class="fas fa-hourglass-half" style="margin-right:4px;${iconColor}"></i>Dias úteis restantes: ${dRestantes}</span>
                <span style="color:#cbd5e1;">|</span>
                <span><i class="fas fa-calendar-alt" style="margin-right:4px;${iconColor}"></i>Total de dias úteis no mês: ${dTotal}</span>
            </div>`;
        }

        textoEl.style.display = 'block';
        textoEl.innerHTML = `
        <div style="display:flex;flex-direction:column;">
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                <strong style="font-size:14px;color:var(--text-main);">Baixas até ${ultimaBaixa}</strong>${tagDu} 
                <span style="font-size:11.5px;color:var(--text-muted);margin-left:4px;font-weight:500;">(Feito/Dia e projeção calculados até esta data de baixas do banco)</span>
            </div>
            ${extrasHtml}
        </div>`;
        
        bannerEl.style.display = 'flex';
        bannerEl.style.alignItems = 'flex-start';
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

let _carregandoPontoDropdown = false;
let _todosOperadoresDropdownPonto = [];

/**
 * Carrega a lista de operadores no dropdown da tela de horários do Admin.
 * Respeita o filtro de Banco (SEMEAR/AGORACRED) e o checkbox 'Somente Ativos'.
 */
async function carregarOperadoresDropdownPontoAdm() {
    const selectEl = document.getElementById('adm-filtro-operador-ponto');
    if (!selectEl) return;

    if (_carregandoPontoDropdown) return;
    _carregandoPontoDropdown = true;

    // Lê o banco selecionado (SEMEAR ou AGORACRED)
    const selectBanco = document.getElementById('adm-filtro-banco-ponto');
    const bancoSelecionado = selectBanco ? selectBanco.value : 'SEMEAR';

    // Lê o estado do checkbox de somente ativos (padrão: marcado)
    const checkboxAtivos = document.getElementById('adm-ponto-somente-ativos');
    const somentAtivos = checkboxAtivos ? checkboxAtivos.checked : true;
    const qsAtivos = somentAtivos ? '&somente_ativos=true' : '';

    try {
        const response = await fetch(`/api/operadores?banco=${encodeURIComponent(bancoSelecionado)}${qsAtivos}`);
        const data = await response.json();

        let operadores = [];
        if (data.success && data.data) {
            operadores = data.data;
        }

        // Remove duplicados por login
        const mapaOps = new Map();
        operadores.forEach(op => {
            if (op.login && !mapaOps.has(op.login.toLowerCase())) {
                mapaOps.set(op.login.toLowerCase(), op);
            }
        });

        // Adiciona o próprio admin caso não esteja na lista
        const loginAdmin = window.operadorAdmLogado?.login || '';
        const nomeAdmin = window.operadorAdmLogado?.nome || 'Administrador';
        if (!mapaOps.has(loginAdmin.toLowerCase())) {
            mapaOps.set(loginAdmin.toLowerCase(), { login: loginAdmin, nome: nomeAdmin });
        }

        const opsUnicos = Array.from(mapaOps.values());
        opsUnicos.sort((a, b) => (a.nome || a.login).localeCompare(b.nome || b.login));
        _todosOperadoresDropdownPonto = opsUnicos;

        // Se o operador atualmente selecionado não pertence ao novo banco filtrado, reseta para o admin
        const inputOculto = document.getElementById('adm-filtro-operador-ponto');
        const opAtualNaLista = opsUnicos.some(o => o.login.toLowerCase() === (inputOculto?.value || '').toLowerCase());

        if (inputOculto && (!inputOculto.value || !opAtualNaLista)) {
            inputOculto.value = loginAdmin;
        }

        _renderizarListaOperadoresPonto(opsUnicos);

        // Atualiza o texto do botão com o operador padrão
        _atualizarBotaoOpDropdown(inputOculto?.value || loginAdmin);

        // Fecha painel ao clicar fora
        document.removeEventListener('mousedown', _fecharDropdownOpFora);
        document.addEventListener('mousedown', _fecharDropdownOpFora);

        // Carrega os dados do operador selecionado no momento
        const loginSelecionado = inputOculto?.value || loginAdmin;
        _carregandoPontoDropdown = false;
        if (loginSelecionado) {
            await carregarPontoAdm(loginSelecionado, true);
        }

    } catch (err) {
        _carregandoPontoDropdown = false;
        console.error('Erro ao carregar lista de operadores para dropdown do ponto:', err);
    }
}

/**
 * Renderiza os itens da lista no custom dropdown de operadores.
 */
function _renderizarListaOperadoresPonto(lista) {
    const ulEl = document.getElementById('adm-ponto-op-lista');
    if (!ulEl) return;
    const loginAtual = document.getElementById('adm-filtro-operador-ponto')?.value || '';
    const loginAdmin = window.operadorAdmLogado?.login || '';
    const nomeAdmin = window.operadorAdmLogado?.nome || 'Administrador';

    const itemReset = `<li onclick="selecionarOperadorPonto('${loginAdmin}', '${nomeAdmin.replace(/'/g, "\\'")}')"
        style="padding: 9px 14px; cursor: pointer; font-size: 13px; font-weight: 600; color: var(--purple-main); background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 8px;">
        <i class="fas fa-user-circle"></i>
        <span>Restaurar meu perfil (${nomeAdmin.split(' ')[0]})</span>
    </li>`;

    const itensLista = lista.map(op => {
        const isSel = op.login.toLowerCase() === loginAtual.toLowerCase();
        return `<li onclick="selecionarOperadorPonto('${op.login}', '${(op.nome || op.login).replace(/'/g, "\\'")}')"
                    style="padding: 9px 14px; cursor: pointer; font-size: 13px; font-weight: ${isSel ? '700' : '500'};
                           color: ${isSel ? 'var(--purple-main)' : 'var(--text-main)'};
                           background: ${isSel ? 'rgba(126,61,151,0.08)' : 'transparent'};
                           border-left: 3px solid ${isSel ? 'var(--purple-main)' : 'transparent'};
                           transition: all 0.15s;"
                    onmouseenter="this.style.background='rgba(126,61,151,0.06)'"
                    onmouseleave="this.style.background='${isSel ? 'rgba(126,61,151,0.08)' : 'transparent'}'">
                  ${op.nome || op.login} <span style="color:#94a3b8;font-size:11px;">(${op.login})</span>
                </li>`;
    }).join('');

    ulEl.innerHTML = itemReset + (itensLista || '<li style="padding:12px 14px;color:#94a3b8;font-size:13px;">Nenhum operador encontrado</li>');
}


/**
 * Atualiza o texto do botão do custom dropdown com o nome do operador selecionado.
 */
function _atualizarBotaoOpDropdown(login) {
    const btn = document.getElementById('adm-ponto-op-btn');
    if (!btn) return;
    const op = _todosOperadoresDropdownPonto.find(o => o.login.toLowerCase() === login.toLowerCase());
    const textoBotao = op ? `${op.nome || op.login}` : login;
    btn.innerHTML = `${textoBotao} <span style="position:absolute;right:10px;top:50%;transform:translateY(-50%);pointer-events:none;">▾</span>`;
}

/**
 * Abre/fecha o painel do custom dropdown de operadores.
 */
function togglePontoOpDropdown() {
    const panel = document.getElementById('adm-ponto-op-panel');
    if (!panel) return;
    const aberto = panel.style.display !== 'none';
    if (aberto) {
        panel.style.display = 'none';
    } else {
        panel.style.display = 'block';
        // Limpa busca ao abrir
        const busca = document.getElementById('adm-ponto-op-busca');
        if (busca) {
            busca.value = '';
            _renderizarListaOperadoresPonto(_todosOperadoresDropdownPonto);
            setTimeout(() => busca.focus(), 50);
        }
    }
}

/**
 * Fecha o custom dropdown ao clicar fora dele.
 */
function _fecharDropdownOpFora(event) {
    const container = document.getElementById('adm-ponto-op-dropdown');
    if (container && !container.contains(event.target)) {
        const panel = document.getElementById('adm-ponto-op-panel');
        if (panel) panel.style.display = 'none';
    }
}

/**
 * Seleciona um operador no custom dropdown e carrega os dados de ponto.
 */
function selecionarOperadorPonto(login, nome) {
    const inputOculto = document.getElementById('adm-filtro-operador-ponto');
    if (inputOculto) inputOculto.value = login;

    _atualizarBotaoOpDropdown(login);
    _renderizarListaOperadoresPonto(_todosOperadoresDropdownPonto);

    // Fecha o painel
    const panel = document.getElementById('adm-ponto-op-panel');
    if (panel) panel.style.display = 'none';

    carregarPontoAdm(login, true);
}

/**
 * Filtra a lista de operadores no painel à medida que o usuário digita.
 */
function filtrarOperadoresPontoPorTexto(termo) {
    if (!_todosOperadoresDropdownPonto.length) return;
    const t = (termo || '').trim().toLowerCase();
    const filtrados = _todosOperadoresDropdownPonto.filter(op => {
        return (op.nome || '').toLowerCase().includes(t) || (op.login || '').toLowerCase().includes(t);
    });
    _renderizarListaOperadoresPonto(filtrados);
}


/**
 * Carrega os dados de ponto eletrônico de um operador específico para a visão do Admin.
 */
async function carregarPontoAdm(loginAlvo, skipPopularDropdown = false) {
    const inputOculto = document.getElementById('adm-filtro-operador-ponto');

    // Se o dropdown ainda estiver vazio e não foi marcado para pular, popula primeiro
    if (!skipPopularDropdown && _todosOperadoresDropdownPonto.length === 0) {
        await carregarOperadoresDropdownPontoAdm();
        return;
    }

    const login = loginAlvo || inputOculto?.value || window.operadorAdmLogado?.login || '';

    try {
        const response = await fetch(`/api/horarios/${login}`);
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }
        const result = await response.json();


        if (!result.success || !result.data) {
            console.error('Erro ao carregar horarios no admin:', result.message);
            return;
        }

        const data = result.data;
        const ponto = data.ponto || {};
        const cardD1 = ponto.card_d1 || {};
        const historico = ponto.historico_mes || [];

        // Atualiza foto do operador no cabeçalho
        const elFoto = document.getElementById('ponto-adm-foto');
        const elFotoFallback = document.getElementById('ponto-adm-foto-fallback');
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

        // Atualiza perfil do topo
        const elNome = document.getElementById('ponto-adm-nome');
        const elTempoCasa = document.getElementById('ponto-adm-tempo-casa');
        const elBanco = document.getElementById('ponto-adm-banco');
        const elDataRef = document.getElementById('ponto-adm-data-ref');
        const elAtualizacao = document.getElementById('ponto-adm-ultima-atualizacao');

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
        const elBancoHoras = document.getElementById('card-adm-ponto-banco-horas');
        const elEnt1 = document.getElementById('card-adm-ponto-ent1');
        const elSai1 = document.getElementById('card-adm-ponto-sai1');
        const elEnt2 = document.getElementById('card-adm-ponto-ent2');
        const elSai2 = document.getElementById('card-adm-ponto-sai2');

        if (elBancoHoras) {
            const saldo = cardD1.b_saldo || '00:00';
            const ehNegativo = saldo.startsWith('-');
            const corSaldo = ehNegativo ? '#ef4444' : '#10b981';

            elBancoHoras.textContent = saldo;
            elBancoHoras.style.color = corSaldo;

            const cardContainer = document.getElementById('card-adm-banco-container');
            const cardIcon = document.getElementById('card-adm-banco-icon');
            if (cardContainer) cardContainer.style.borderTopColor = corSaldo;
            if (cardIcon) cardIcon.style.color = corSaldo;

            // Atualiza também o saldo do Banco de Horas no cabeçalho do perfil do topo direito
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
        const tbody = document.getElementById('tabela-ponto-adm');
        if (!tbody) return;

        if (historico.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted);">Nenhum lançamento encontrado para o mês atual deste operador.</td></tr>`;
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
        console.error('Erro ao carregar ponto no admin:', err);
    }
}

// Expõe para chamadas globais/onclick
window.carregarPontoAdm                      = carregarPontoAdm;
window.carregarOperadoresDropdownPontoAdm    = carregarOperadoresDropdownPontoAdm;

// ================================================================
// A função renderizarTrimestreDUAdm(banco, dados) está definida
// nas linhas acima (~315-390) e é a versão correta com mapeamento bancoâ†’ID.



// ================================================================
// FILTRAR PELO DU ATUAL — BOTÃƒO "ATÃ‰ DU ATUAL" — ADM
// ================================================================
// Calcula e preenche os inputs de DU e recarrega toda a página ADM.

function filtrarDUAtualAdm() {
    const duFimEl = document.getElementById('filtro-du-fim-adm');
    const duInicioEl = document.getElementById('filtro-du-inicio-adm');
    if (!duFimEl || !duInicioEl) return;

    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = hoje.getMonth();
    let duContador = 0;

    for (let d = 1; d <= hoje.getDate(); d++) {
        const dia = new Date(ano, mes, d);
        const dow = dia.getDay();
        if (dow >= 1 && dow <= 5) duContador++;
    }

    duInicioEl.value = 1;
    duFimEl.value = Math.max(1, duContador);

    if (typeof carregarDadosAdm === 'function') carregarDadosAdm();
}
window.filtrarDUAtualAdm = filtrarDUAtualAdm;

// ================================================================
// EXPORT - CSV DAS FAIXAS (Recebimento por Operador × Faixa de Atraso — SEMEAR)
// ================================================================

/**
 * Exporta para CSV a tabela de Recebimento por Operador × Faixa de Atraso (SEMEAR).
 * Lê os dados de window._faixasAdmSemear preenchido ao renderizar o dashboard.
 */
function exportarFaixasCSV() {
    const dados = window._faixasAdmSemear || [];
    if (!dados || dados.length === 0) {
        alert('Nenhum dado de faixas para exportar.');
        return;
    }

    // As chaves de fases são as mesmas usadas em renderizarFaixasSemear
    // O backend retorna {operador, imagem, 'Fase 10 a 30': valor, 'Fase 10 a 30_qtd': qtd, ...}
    const faixasCols = [
        'Fase 10 a 30', 'Fase 31 a 60', 'Fase 61 a 90', 'Fase 91 a 120',
        'Fase 121 a 180', 'Fase 181 a 240', 'Fase 241 a 360',
        'Fase 361 a 720', 'Fase 721 a 1080', 'Fase 1081 a 1440',
        'Fase 1441 a 1800', '> 1800'
    ];

    const cabecalhos = ['Operador', ...faixasCols, 'Total (R$)'];

    const linhas = dados.map(op => {
        const valores = faixasCols.map(f => {
            const v = op[f] || 0;
            return (typeof v === 'number' ? v : 0).toFixed(2).replace('.', ',');
        });
        // Calcula total somando todos os valores de faixas
        const total = faixasCols.reduce((acc, f) => acc + (op[f] || 0), 0);
        return [`"${(op.operador || '').replace(/"/g, '""')}"`, ...valores, total.toFixed(2).replace('.', ',')].join(';');
    });

    // Linha de totais
    const totais = faixasCols.map(f =>
        dados.reduce((acc, op) => acc + (op[f] || 0), 0).toFixed(2).replace('.', ',')
    );
    const totalGeral = faixasCols.reduce((acc, f) =>
        acc + dados.reduce((s, op) => s + (op[f] || 0), 0), 0
    ).toFixed(2).replace('.', ',');
    linhas.push(['"TOTAL"', ...totais, totalGeral].join(';'));

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    _dispararDownloadCSV(csv, `faixas_semear_${new Date().toISOString().split('T')[0]}.csv`);
}

// ================================================================
// EXPORT - CSV DO COMPARATIVO TRIMESTRAL POR DIA ÚTIL
// ================================================================

/**
 * Exporta para CSV o Comparativo Trimestral por Dia Útil do banco especificado.
 * @param {string} banco - 'semear' ou 'agoracred'
 */
function exportarTrimestreCSV(banco) {
    const dados = banco === 'semear'
        ? (window._trimestreDUSemear || null)
        : (window._trimestreDUAgoracred || null);

    if (!dados || !dados.linhas || dados.linhas.length === 0) {
        alert('Nenhum dado trimestral para exportar.');
        return;
    }

    // O backend retorna: colunas, linhas[{dia_util, data_atual, v_atual, v_m1, v_m2}],
    // totais: {total_atual, total_m1, total_m2}
    const colunas = dados.colunas || ['Mês Atual', 'M-1', 'M-2'];
    const cabecalhos = ['Dia Útil', 'Data', colunas[0] || 'Mês Atual', colunas[1] || 'M-1', colunas[2] || 'M-2'];

    const linhas = dados.linhas.map(linha => [
        linha.dia_util || linha.du || '',
        linha.data_atual || linha.data || '',
        (linha.v_atual || linha.m0 || 0).toFixed(2).replace('.', ','),
        (linha.v_m1   || linha.m1 || 0).toFixed(2).replace('.', ','),
        (linha.v_m2   || linha.m2 || 0).toFixed(2).replace('.', ',')
    ].join(';'));

    // Linha de totais
    if (dados.totais) {
        const t = dados.totais;
        linhas.push([
            'TOTAL', '',
            (t.total_atual || t.v_atual || t.m0 || 0).toFixed(2).replace('.', ','),
            (t.total_m1   || t.v_m1   || t.m1 || 0).toFixed(2).replace('.', ','),
            (t.total_m2   || t.v_m2   || t.m2 || 0).toFixed(2).replace('.', ',')
        ].join(';'));
    }

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    _dispararDownloadCSV(csv, `trimestral_${banco.toUpperCase()}_${new Date().toISOString().split('T')[0]}.csv`);
}

// ================================================================
// EXPORT - CSV DA EVOLUÇÃO DIÁRIA POR BANCO
// ================================================================

/**
 * Exporta para CSV a tabela de Valores Diários por Banco (SEMEAR + AGORACRED + Total).
 * Cruza os dados de evolução diária de ambos os bancos.
 */
function exportarEvolucaoDiariaCSV() {
    const semear    = window._evolucaoDiariaAdmSemear   || [];
    const agoracred = window._evolucaoDiariaAdmAgoracred || [];

    if (semear.length === 0 && agoracred.length === 0) {
        alert('Nenhum dado de evolução diária para exportar.');
        return;
    }

    // Constrói mapa por data — o backend retorna {data, total, quantidade, data_formatada}
    const mapaData = {};
    semear.forEach(d => {
        const k = d.data || '';
        if (!k) return;
        if (!mapaData[k]) mapaData[k] = { data: k, dataFmt: d.data_formatada || k, semear: 0, agoracred: 0 };
        mapaData[k].semear = d.total || d.valor || d.faturamento || 0;
    });
    agoracred.forEach(d => {
        const k = d.data || '';
        if (!k) return;
        if (!mapaData[k]) mapaData[k] = { data: k, dataFmt: d.data_formatada || k, semear: 0, agoracred: 0 };
        mapaData[k].agoracred = d.total || d.valor || d.faturamento || 0;
    });

    const cabecalhos = ['Data (YYYY-MM-DD)', 'Dia', 'SEMEAR (R$)', 'AGORACRED (R$)', 'TOTAL (R$)'];
    const linhas = Object.values(mapaData)
        .sort((a, b) => (a.data > b.data ? 1 : -1))
        .map(d => [
            d.data,
            `"${d.dataFmt}"`,
            (d.semear    || 0).toFixed(2).replace('.', ','),
            (d.agoracred || 0).toFixed(2).replace('.', ','),
            ((d.semear || 0) + (d.agoracred || 0)).toFixed(2).replace('.', ',')
        ].join(';'));

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    _dispararDownloadCSV(csv, `evolucao_diaria_${new Date().toISOString().split('T')[0]}.csv`);
}

// ================================================================
// EXPORT - CSV DA EVOLUÇÃO DE OPERADORES (Variação vs Mês Anterior)
// ================================================================

/**
 * Exporta para CSV a tabela de Evolução dos Operadores — Variação vs Mês Anterior.
 */
function exportarEvolucaoOperadoresCSV() {
    const dados = window._evolucaoOperadoresAdm || [];
    if (!dados || dados.length === 0) {
        alert('Nenhum dado de evolução de operadores para exportar.');
        return;
    }

    const cabecalhos = ['Banco', 'Operador', 'Fat. Atual (R$)', 'Fat. Anterior (R$)',
                        'Dif. (R$)', 'Var. (%)', '% Meta Atual', '% Meta Ant.',
                        'Dif. Meta (pp)', 'Projeção (R$)', '% Projeção'];

    const linhas = dados.map(op => [
        op.banco || '',
        `"${(op.operador || '').replace(/"/g, '""')}"`,
        (op.fat_atual    || 0).toFixed(2).replace('.', ','),
        (op.fat_anterior || 0).toFixed(2).replace('.', ','),
        (op.variacao     || 0).toFixed(2).replace('.', ','),
        (op.variacao_percentual || 0).toFixed(1).replace('.', ',') + '%',
        (op.perc_meta_atual    || 0).toFixed(1).replace('.', ',') + '%',
        (op.perc_meta_anterior || 0).toFixed(1).replace('.', ',') + '%',
        (op.variacao_meta_pp   || 0).toFixed(1).replace('.', ',') + ' pp',
        (op.projecao            || 0).toFixed(2).replace('.', ','),
        (op.projecao_percentual != null ? op.projecao_percentual : (op.meta > 0 ? (op.projecao / op.meta) * 100 : 0)).toFixed(1).replace('.', ',') + '%'
    ].join(';'));

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    _dispararDownloadCSV(csv, `evolucao_operadores_${new Date().toISOString().split('T')[0]}.csv`);
}

// ================================================================
// EXPORT - HELPER: dispara download de blob CSV
// ================================================================

/**
 * Cria um link temporário e dispara o download de um CSV.
 * @param {string} csvContent - Conteúdo CSV (com BOM UTF-8 se necessário)
 * @param {string} filename   - Nome do arquivo
 */
function _dispararDownloadCSV(csvContent, filename) {
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

// Expõe funções de exportação ao escopo global
window.exportarFaixasCSV             = exportarFaixasCSV;
window.exportarTrimestreCSV          = exportarTrimestreCSV;
window.exportarEvolucaoDiariaCSV     = exportarEvolucaoDiariaCSV;
window.exportarEvolucaoOperadoresCSV = exportarEvolucaoOperadoresCSV;
window.exportarMatrizFaixasCSV       = exportarMatrizFaixasCSV;

// ================================================================
// BANNER ALTO × BAIXO ATRASO (SEMEAR)
// Calcula e exibe o resumo de baixo atraso (≤360d) vs alto atraso (>360d)
// usando os dados já disponíveis em window._faixasAdmSemear
// ================================================================

/**
 * Atualiza o banner de distribuição Alto × Baixo Atraso.
 * @param {Array} faixas - lista de operadores com valores por fase
 */
function atualizarBannerAltoBaixoAtraso(faixas) {
    const banner = document.getElementById('banner-alto-baixo-atraso-semear');
    if (!banner) return;

    const faixasBaixo = ['Fase 10 a 30','Fase 31 a 60','Fase 61 a 90','Fase 91 a 120','Fase 121 a 180','Fase 181 a 240','Fase 241 a 360'];
    const faixasAlto  = ['Fase 361 a 720','Fase 721 a 1080','Fase 1081 a 1440','Fase 1441 a 1800','> 1800'];

    const totalBaixo = faixasBaixo.reduce((acc, f) =>
        acc + faixas.reduce((s, op) => s + (op[f] || 0), 0), 0);
    const totalAlto  = faixasAlto.reduce((acc, f) =>
        acc + faixas.reduce((s, op) => s + (op[f] || 0), 0), 0);
    const totalGeral = totalBaixo + totalAlto;

    const pctBaixo = totalGeral > 0 ? (totalBaixo / totalGeral * 100).toFixed(1) : '0.0';
    const pctAlto  = totalGeral > 0 ? (totalAlto  / totalGeral * 100).toFixed(1) : '0.0';

    banner.style.display = 'flex';
    banner.innerHTML = `
        <div style="flex:1;min-width:200px;background:linear-gradient(135deg,#d1fae5,#a7f3d0);border-radius:12px;padding:16px 20px;border-left:5px solid #10b981;">
            <div style="font-size:11px;font-weight:700;color:#065f46;letter-spacing:.5px;margin-bottom:6px;">🟢 BAIXO ATRASO — ATÉ 360 DIAS</div>
            <div style="font-size:22px;font-weight:900;color:#065f46;">${formatarMoeda(totalBaixo)}</div>
            <div style="font-size:12px;color:#047857;margin-top:4px;">${pctBaixo}% do recebimento total</div>
            <div style="background:#10b981;border-radius:4px;height:6px;margin-top:8px;width:${pctBaixo}%;"></div>
        </div>
        <div style="flex:1;min-width:200px;background:linear-gradient(135deg,#fee2e2,#fecaca);border-radius:12px;padding:16px 20px;border-left:5px solid #ef4444;">
            <div style="font-size:11px;font-weight:700;color:#991b1b;letter-spacing:.5px;margin-bottom:6px;">🔴 ALTO ATRASO — ACIMA DE 360 DIAS</div>
            <div style="font-size:22px;font-weight:900;color:#991b1b;">${formatarMoeda(totalAlto)}</div>
            <div style="font-size:12px;color:#b91c1c;margin-top:4px;">${pctAlto}% do recebimento total</div>
            <div style="background:#ef4444;border-radius:4px;height:6px;margin-top:8px;width:${pctAlto}%;"></div>
        </div>
    `;
}
window.atualizarBannerAltoBaixoAtraso = atualizarBannerAltoBaixoAtraso;

// ================================================================
// EXPORT - CSV DA MATRIZ FAIXAS VS MÊS
// ================================================================

/**
 * Exporta para CSV a tabela Faixa de Atraso vs Mês — Visão Anual SEMEAR.
 * Lê window._matrizFaixasAdm gravado em renderizarMatrizFaixasAdm().
 */
function exportarMatrizFaixasCSV() {
    const dados = window._matrizFaixasAdm || null;
    if (!dados || !dados.linhas || dados.linhas.length === 0) {
        alert('Nenhum dado de matriz de faixas para exportar.');
        return;
    }

    const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
    const cabecalhos = ['Faixa de Atraso', ...meses, 'Total Ano'];

    const linhas = dados.linhas.map(linha => [
        `"${(linha.faixa || '').replace(/"/g,'""')}"`,
        ...meses.map(m => (linha[m] || 0).toFixed(2).replace('.',',')),
        (linha.total_ano || 0).toFixed(2).replace('.',',')
    ].join(';'));

    if (dados.totais) {
        const t = dados.totais;
        linhas.push([
            '"TOTAL GERAL"',
            ...meses.map(m => (t[m] || 0).toFixed(2).replace('.',',')),
            (t.total_ano || 0).toFixed(2).replace('.',',')
        ].join(';'));
    }

    const csv = '\uFEFF' + [cabecalhos.join(';'), ...linhas].join('\n');
    _dispararDownloadCSV(csv, `faixa_vs_mes_semear_${new Date().toISOString().split('T')[0]}.csv`);
}
window.exportarMatrizFaixasCSV = exportarMatrizFaixasCSV;

// ================================================================
// VISÃO PERIÓDICA — Faixas ≤360 / >360 (SEMEAR)
// ================================================================

/**
 * Renderiza mini-cards de faixa de atraso na Visão Periódica do admin.
 * Só exibe para banco SEMEAR; oculta para AGORACRED e CONSOLIDADO.
 */
function renderizarFaixasPeriodica(faixas, banco) {
    const container = document.getElementById('container-faixas-periodica-adm');
    if (!container) return;
    if (!faixas || banco !== 'SEMEAR') {
        container.style.display = 'none';
        return;
    }
    const ate   = faixas.ate_360   || {};
    const acima = faixas.acima_360 || {};
    container.style.display = 'block';
    container.innerHTML = `
    <div style="margin-top:16px;border-top:1px solid #e5e7eb;padding-top:14px;">
        <div style="font-size:12px;font-weight:700;color:#7e3d97;letter-spacing:.5px;margin-bottom:10px;">
            <i class="fas fa-layer-group"></i> FAIXAS DE ATRASO NO PERÍODO
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <div style="flex:1;min-width:160px;background:linear-gradient(135deg,#d1fae5,#a7f3d0);border-radius:10px;padding:12px 16px;border-left:4px solid #10b981;">
                <div style="font-size:10px;font-weight:700;color:#065f46;letter-spacing:.5px;margin-bottom:4px;">🟢 ATÉ 360 DIAS</div>
                <div style="font-size:18px;font-weight:900;color:#065f46;">${formatarMoeda(ate.total || 0)}</div>
                <div style="font-size:11px;color:#047857;margin-top:2px;">${ate.qtd || 0} pgtos · ${ate.percentual || 0}%</div>
            </div>
            <div style="flex:1;min-width:160px;background:linear-gradient(135deg,#fee2e2,#fecaca);border-radius:10px;padding:12px 16px;border-left:4px solid #ef4444;">
                <div style="font-size:10px;font-weight:700;color:#991b1b;letter-spacing:.5px;margin-bottom:4px;">🔴 ACIMA DE 360 DIAS</div>
                <div style="font-size:18px;font-weight:900;color:#991b1b;">${formatarMoeda(acima.total || 0)}</div>
                <div style="font-size:11px;color:#b91c1c;margin-top:2px;">${acima.qtd || 0} pgtos · ${acima.percentual || 0}%</div>
            </div>
        </div>
    </div>`;
}
window.renderizarFaixasPeriodica = renderizarFaixasPeriodica;

// ================================================================
// VISÃO MÊS × OPERADOR (pivot table)
// ================================================================

/**
 * Renderiza tabela pivô Operador × Mês com faturamento e % meta de cada operador por mês.
 * @param {Array}  operadores  - lista do ranking (semear ou agoracred)
 * @param {string} banco       - 'SEMEAR' | 'AGORACRED'
 */
function renderizarMesOperadorAdm(operadores, banco) {
    const tbody  = document.getElementById('tabela-mes-operador-adm');
    const titulo = document.getElementById('titulo-mes-operador-adm');
    const card   = document.getElementById('card-mes-operador-adm');
    if (!tbody || !card) return;

    const cor = banco === 'AGORACRED' ? '#10b981' : '#7E3E9A';
    if (titulo) titulo.textContent = `Recebimento Mensal por Operador — ${banco}`;

    const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
    const mesAtual = new Date().getMonth(); // 0-indexed

    if (!operadores || operadores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="14" style="text-align:center;color:#9ca3af;padding:20px;">Nenhum dado disponível para este banco</td></tr>';
        card.style.display = 'block';
        return;
    }

    let html = '';
    operadores.forEach((op, idx) => {
        const bg       = idx % 2 === 0 ? '#ffffff' : (banco === 'AGORACRED' ? '#f0fdf4' : '#faf5ff');
        const bgSticky = idx % 2 === 0 ? '#ffffff' : (banco === 'AGORACRED' ? '#f0fdf4' : '#faf5ff');
        // Backend retorna: { login, meses: { Jan: {fat, meta, perc}, ... } }
        const mesMap = op.meses || {};
        const nomeOp = op.login || op.operador || '-';

        // PRIMEIRO TD: nome do operador — sticky para permanecer visível durante o scroll horizontal
        let row = `<tr style="background:${bg};">
            <td style="padding:8px 12px;font-weight:700;white-space:nowrap;border-right:2px solid #e5e7eb;text-align:left;color:#1f2937;font-size:12px;position:sticky;left:0;z-index:5;background:${bgSticky};box-shadow:2px 0 4px rgba(0,0,0,0.06);min-width:150px;width:150px;">${nomeOp}</td>`;

        meses.forEach((nomeMes, i) => {
            const m = mesMap[nomeMes];
            const isFuturo = i > mesAtual;
            if (isFuturo) {
                row += `<td style="padding:6px 4px;text-align:center;color:#d1d5db;background:#fafafa;min-width:70px;">—</td>`;
            } else if (m && (m.fat > 0 || m.meta > 0)) {
                const perc    = (m.perc || 0).toFixed(1);
                const percNum = parseFloat(perc);
                const percCor = percNum >= 100 ? '#16a34a' : percNum >= 70 ? '#d97706' : '#dc2626';
                const percBg  = percNum >= 100 ? '#f0fdf4' : percNum >= 70 ? '#fffbeb' : '#fef2f2';
                row += `<td style="padding:6px 4px;text-align:center;vertical-align:middle;min-width:70px;border-bottom:1px solid #f3f4f6;">
                    <div style="font-size:11px;font-weight:700;color:#111827;">${formatarMoeda(m.fat || 0)}</div>
                    <span style="font-size:10px;font-weight:700;color:${percCor};background:${percBg};border-radius:10px;padding:1px 5px;display:inline-block;margin-top:2px;border:1px solid ${percCor}20;">${perc}%</span>
                </td>`;
            } else {
                row += `<td style="padding:6px 4px;text-align:center;color:#9ca3af;min-width:70px;">—</td>`;
            }
        });
        row += '</tr>';
        html += row;
    });

    tbody.innerHTML = html;
    card.style.display = 'block';
}
window.renderizarMesOperadorAdm = renderizarMesOperadorAdm;