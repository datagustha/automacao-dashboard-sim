/**
 * COMPONENTES - Cards, Tabelas, Gráficos
 * =======================================
 */

// ================================================================
// CARDS
// ================================================================

function criarCard(titulo, valor, id, icone, cor, subtexto = null) {
    const cores = {
        purple: 'purple',
        green: 'green',
        blue: 'blue',
        orange: 'orange',
        red: 'red'
    };
    
    const corClasse = cores[cor] || 'purple';
    
    let html = `
        <div class="card" style="border-left: 4px solid var(--purple-main);">
            <div class="card-icon-wrapper ${corClasse}">
                <i class="fas ${icone}"></i>
            </div>
            <div class="card-content">
                <span class="card-title" style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;">${titulo}</span>
                <span class="card-value" id="${id}" style="font-size:28px;font-weight:700;color:var(--text-main);">${valor}</span>
    `;
    
    if (subtexto) {
        html += `<span class="card-sub" id="${id}-sub" style="font-size:12px;color:var(--text-muted);margin-top:4px;display:block;">${subtexto}</span>`;
    }
    
    html += `</div></div>`;
    return html;
}

function criarCardMeta(titulo, idValor, idBarra, idPercentual, idFooter, meta, cor = 'purple') {
    const cores = {
        purple: 'var(--purple-main)',
        green: 'var(--emerald)',
        orange: '#d97706',
        blue: '#2563eb'
    };
    
    const corHex = cores[cor] || cores.purple;
    const corBg = corHex + '15';
    
    return `
        <div class="card-meta" style="border-left: 4px solid ${corHex};padding:22px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06);height:100%;">
            <div class="meta-header" style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <i class="fas fa-bullseye" style="color: ${corHex}; font-size: 22px;"></i>
                <span class="meta-title" style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;">${titulo}</span>
            </div>
            <div class="meta-value" id="${idValor}" style="font-size:32px;font-weight:800;color:var(--text-main);margin-bottom:14px;">${meta}</div>
            <div class="meta-bar-wrapper" style="width:100%;background-color:#e5e7eb;border-radius:6px;height:10px;margin-bottom:10px;overflow:hidden;">
                <div class="meta-bar" id="${idBarra}" style="width: 0%; height:10px; border-radius:6px; background: ${corHex}; transition: width 0.6s ease;"></div>
            </div>
            <div class="meta-info" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <span class="meta-label" style="font-size:12px;color:var(--text-muted);font-weight:600;">Meta: <span id="${idValor}-meta" style="font-weight:700;color:var(--text-main);">R$ 0,00</span></span>
                <span class="meta-percent" id="${idPercentual}" style="font-size:18px;font-weight:800;padding:4px 14px;border-radius:20px;color:${corHex};background:${corBg};">0%</span>
            </div>
            <div class="meta-footer" id="${idFooter}" style="font-size:13px;color:var(--text-muted);border-top:1px solid #f0f0f0;padding-top:10px;font-weight:500;min-height:22px;"></div>
        </div>
    `;
}

function criarCardTMA(titulo, idValor, icone, cor, subtextoId = null) {
    const cores = {
        purple: 'purple',
        green: 'green',
        blue: 'blue',
        orange: 'orange'
    };
    
    const corClasse = cores[cor] || 'purple';
    
    let html = `
        <div class="card" style="border-left: 4px solid var(--purple-main);">
            <div class="card-icon-wrapper ${corClasse}">
                <i class="fas ${icone}"></i>
            </div>
            <div class="card-content">
                <span class="card-title" style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;">${titulo}</span>
                <span class="card-value" id="${idValor}" style="font-size:28px;font-weight:700;color:var(--text-main);">—</span>
    `;
    
    if (subtextoId) {
        html += `<span class="card-sub" id="${subtextoId}" style="font-size:12px;color:var(--text-muted);margin-top:4px;display:block;"></span>`;
    }
    
    html += `</div></div>`;
    return html;
}

// ================================================================
// TABELAS
// ================================================================

function criarTabela(id, colunas, dados, pageSize = 10) {
    let html = `
        <div class="table-wrapper">
            <table>
                <thead style="background:var(--purple-main);">
                    <tr>
    `;
    
    colunas.forEach(col => {
        html += `<th style="color:white;padding:12px 16px;text-align:center;">${col}</th>`;
    });
    
    html += `</tr></thead><tbody id="${id}">`;
    
    if (!dados || dados.length === 0) {
        html += `<tr><td colspan="${colunas.length}" style="text-align:center;color:#6B7280;padding:30px;">Nenhum dado encontrado</td></tr>`;
    } else {
        const paginados = dados.slice(0, pageSize);
        paginados.forEach(linha => {
            html += `<tr>`;
            colunas.forEach(col => {
                const valor = linha[col] !== undefined ? linha[col] : '-';
                html += `<td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;">${valor}</td>`;
            });
            html += `</tr>`;
        });
    }
    
    html += `</tbody></table></div>`;
    return html;
}

// ================================================================
// GRÁFICOS - COM APEXCHARTS INTERATIVOS E PREMIUM
// ================================================================

function criarGraficoEvolucao(dados, cor = '#7e3d97') {
    if (!dados || dados.length === 0) {
        return `
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#a0aec0;font-size:14px;">
                <i class="fas fa-chart-line" style="font-size:40px;opacity:0.3;margin-bottom:10px;"></i>
                <span>Sem dados para o período</span>
            </div>
        `;
    }
    
    // Gera um ID único aleatório para evitar colisão de elementos de gráfico
    const uniqueId = 'chart-evolucao-' + Math.random().toString(36).substr(2, 9);
    
    // Agenda a renderização do gráfico após o elemento ser inserido no DOM
    setTimeout(() => {
        const container = document.getElementById(uniqueId);
        if (!container) return;
        
        // Mapeia datas e valores
        const datas = dados.map(d => {
            if (d.dia !== undefined) {
                return String(d.dia); // Formato do operador individual
            }
            if (!d.data) return '';
            const partes = d.data.split('-');
            if (partes.length === 3) {
                return `${partes[2]}/${partes[1]}`; // Retorna DD/MM
            }
            return d.data;
        });
        
        const valores = dados.map(d => {
            if (d.total !== undefined) return d.total;
            if (d.realizado !== undefined) {
                if (typeof d.realizado === 'number') return d.realizado;
                // Converte string formatada "R$ 1.234,56" para float
                const limpo = d.realizado.replace(/[R$\s.]/g, '').replace(',', '.');
                const parsed = parseFloat(limpo);
                return isNaN(parsed) ? 0 : parsed;
            }
            return 0;
        });
        
        // Configurações do ApexCharts
        const options = {
            chart: {
                type: 'area',
                height: '100%',
                width: '100%',
                toolbar: { show: false },
                fontFamily: 'Inter, sans-serif',
                sparkline: { enabled: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800
                }
            },
            stroke: {
                curve: 'smooth',
                width: 3
            },
            colors: [cor],
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.35,
                    opacityTo: 0.05,
                    stops: [0, 95]
                }
            },
            dataLabels: { enabled: false },
            series: [{
                name: 'Faturamento',
                data: valores
            }],
            xaxis: {
                type: 'category',
                categories: datas,
                labels: {
                    rotate: -45,
                    style: { colors: '#374151', fontSize: '11px', fontWeight: 600 }
                },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                labels: {
                    formatter: function(val) {
                        return 'R$ ' + val.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                    },
                    style: { colors: '#374151', fontSize: '12px', fontWeight: 600 }
                }
            },

            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 4,
                padding: { left: 10, right: 10 }
            },
            tooltip: {
                theme: 'light',
                x: { show: true },
                y: {
                    formatter: function(val) {
                        return 'R$ ' + val.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
                    }
                }
            }
        };
        
        const chart = new ApexCharts(container, options);
        chart.render();
    }, 50);
    
    return `<div id="${uniqueId}" style="width:100%;height:100%;"></div>`;
}

function criarGraficoFase(dados) {
    if (!dados || dados.length === 0) {
        return `
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#a0aec0;font-size:14px;">
                <i class="fas fa-chart-bar" style="font-size:40px;opacity:0.3;margin-bottom:10px;"></i>
                <span>Sem dados para o período</span>
            </div>
        `;
    }

    // Ordena do maior para o menor valor, para facilitar a leitura
    const dadosOrdenados = [...dados].sort((a, b) => (b.total || 0) - (a.total || 0));

    // Gera um ID único aleatório
    const uniqueId = 'chart-fase-' + Math.random().toString(36).substr(2, 9);

    // Agenda a renderização do gráfico
    setTimeout(() => {
        const container = document.getElementById(uniqueId);
        if (!container) return;

        const labels = dadosOrdenados.map(d => d.fase || 'Outros');
        const valores = dadosOrdenados.map(d => d.total || 0);
        const total = valores.reduce((a, b) => a + b, 0);

        const options = {
            chart: {
                type: 'bar',
                height: '100%',
                width: '100%',
                toolbar: { show: false },
                fontFamily: 'Inter, sans-serif'
            },
            plotOptions: {
                bar: {
                    horizontal: true,
                    barHeight: '65%',
                    distributed: true,
                    dataLabels: { position: 'top' }
                }
            },
            colors: ['#7e3d97', '#9b5bad', '#c084d0', '#d8b4e0', '#e9d8fd', '#d97706', '#f59e0b'],
            series: [{ name: 'Faturamento', data: valores }],
            xaxis: {
                type: 'category',
                categories: labels,
                labels: {
                    style: { colors: '#6B7280', fontSize: '10px', fontWeight: 500 },
                    formatter: function(val) {
                        return 'R$ ' + Math.round(val).toLocaleString('pt-BR');
                    }
                },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                labels: {
                    style: { colors: '#374151', fontSize: '11px', fontWeight: 600 }
                }
            },
            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 4
            },
            legend: { show: false },
            dataLabels: {
                enabled: true,
                formatter: function(val) {
                    return 'R$ ' + parseFloat(val).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                },
                style: { fontSize: '10px', colors: ['#374151'] },
                offsetX: 20
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        const pct = total > 0 ? ((val / total) * 100).toFixed(1) : '0.0';
                        return 'R$ ' + val.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) + ` (${pct}%)`;
                    }
                }
            }
        };

        const chart = new ApexCharts(container, options);
        chart.render();
    }, 50);

    return `<div id="${uniqueId}" style="width:100%;height:100%;min-height:220px;"></div>`;
}

function criarGraficoBarras(dados, x, y, titulo, cor = '#7e3d97') {
    if (!dados || dados.length === 0) {
        return `
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#a0aec0;font-size:14px;">
                <i class="fas fa-chart-bar" style="font-size:40px;opacity:0.3;margin-bottom:10px;"></i>
                <span>Sem dados para exibir</span>
            </div>
        `;
    }
    
    // Gera um ID único aleatório
    const uniqueId = 'chart-bar-' + Math.random().toString(36).substr(2, 9);
    
    // Agenda a renderização
    setTimeout(() => {
        const container = document.getElementById(uniqueId);
        if (!container) return;
        
        const categorias = dados.map(d => d[x] || '-');
        const valores = dados.map(d => d[y] || 0);
        
        const options = {
            chart: {
                type: 'bar',
                height: '100%',
                width: '100%',
                toolbar: { show: false },
                fontFamily: 'Inter, sans-serif'
            },
            colors: [cor],
            series: [{
                name: titulo || 'Faturamento',
                data: valores
            }],
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    columnWidth: '45%',
                    distributed: false
                }
            },
            dataLabels: { enabled: false },
            xaxis: {
                categories: categorias,
                labels: {
                    style: { colors: '#374151', fontSize: '11px', fontWeight: 600 }
                },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                labels: {
                    formatter: function(val) {
                        return 'R$ ' + val.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                    },
                    style: { colors: '#374151', fontSize: '12px', fontWeight: 600 }
                }
            },

            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 4
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return 'R$ ' + val.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
                    }
                }
            }
        };
        
        const chart = new ApexCharts(container, options);
        chart.render();
    }, 50);
    
    return `<div id="${uniqueId}" style="width:100%;height:100%;"></div>`;
}

// ================================================================
// FILTROS
// ================================================================

function criarFiltroDataRange(id) {
    return `
        <div class="filter-group">
            <i class="fas fa-calendar-range"></i>
            <input type="date" id="${id}-inicio" onchange="aplicarFiltro()">
            <span style="color:var(--text-muted);font-size:12px;">até</span>
            <input type="date" id="${id}-fim" onchange="aplicarFiltro()">
        </div>
    `;
}

function criarFiltroBusca(id, placeholder = 'Buscar...') {
    return `
        <div class="filter-group">
            <i class="fas fa-search"></i>
            <input type="text" id="${id}" placeholder="${placeholder}" oninput="aplicarFiltro()">
        </div>
    `;
}

function criarFiltroSelect(id, opcoes, valorPadrao = '') {
    let html = `
        <div class="filter-group">
            <i class="fas fa-filter"></i>
            <select id="${id}" onchange="aplicarFiltro()">
    `;
    
    opcoes.forEach(opcao => {
        const selected = opcao.value === valorPadrao ? 'selected' : '';
        html += `<option value="${opcao.value}" ${selected}>${opcao.label}</option>`;
    });
    
    html += `</select></div>`;
    return html;
}