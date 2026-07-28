/**
 * UTILITÁRIOS - Formatação, Datas, etc.
 * ======================================
 */

// ================================================================
// FORMATAÇÃO DE MOEDA
// ================================================================

function formatarMoeda(valor) {
    if (valor === undefined || valor === null || isNaN(valor)) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// ================================================================
// FORMATAÇÃO DE DATA
// ================================================================

function formatarData(data) {
    if (!data) return '-';
    try {
        const s = String(data).trim();
        // Se vier no formato YYYY-MM-DD (vindo do backend), parseia manualmente
        // para evitar a conversão UTC->local que causa o "bug do dia anterior" (30/06 em vez de 01/07)
        const isoMatch = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
        if (isoMatch) {
            const [, ano, mes, dia] = isoMatch;
            return `${dia}/${mes}/${ano}`;
        }
        const d = new Date(data);
        if (isNaN(d.getTime())) return '-';
        return d.toLocaleDateString('pt-BR');
    } catch {
        return '-';
    }
}

function formatarDataHora(data) {
    if (!data) return '-';
    try {
        const d = new Date(data);
        if (isNaN(d.getTime())) return '-';
        return d.toLocaleString('pt-BR');
    } catch {
        return '-';
    }
}

function formatarDataCompleta(data) {
    if (!data) return '-';
    try {
        const d = new Date(data);
        if (isNaN(d.getTime())) return '-';
        return d.toLocaleDateString('pt-BR', {
            weekday: 'long',
            day: '2-digit',
            month: 'long',
            year: 'numeric'
        });
    } catch {
        return '-';
    }
}

function calcularDUdaData(dataStr) {
    if (!dataStr) return '';
    try {
        let dia, mes, ano;
        const s = String(dataStr).trim();
        if (s.includes('/')) {
            const parts = s.split('/');
            dia = parseInt(parts[0], 10);
            mes = parseInt(parts[1], 10) - 1;
            ano = parseInt(parts[2], 10);
        } else if (s.includes('-')) {
            const parts = s.split('-');
            ano = parseInt(parts[0], 10);
            mes = parseInt(parts[1], 10) - 1;
            dia = parseInt(parts[2].substring(0, 2), 10);
        } else {
            return '';
        }
        if (isNaN(dia) || isNaN(mes) || isNaN(ano)) return '';
        let duCount = 0;
        for (let d = 1; d <= dia; d++) {
            const dt = new Date(ano, mes, d);
            const dow = dt.getDay(); // 0=Dom, 6=Sab
            if (dow >= 1 && dow <= 5) {
                duCount++;
            }
        }
        return duCount > 0 ? `${duCount}º DU` : '';
    } catch {
        return '';
    }
}

// ================================================================
// FORMATAÇÃO DE PERCENTUAL
// ================================================================

function formatarPercentual(valor) {
    if (valor === undefined || valor === null || isNaN(valor)) return '0%';
    return `${parseFloat(valor).toFixed(1)}%`;
}

function formatarPercentualComSinal(valor) {
    if (valor === undefined || valor === null || isNaN(valor)) return '0%';
    const num = parseFloat(valor);
    const sinal = num > 0 ? '+' : '';
    return `${sinal}${num.toFixed(1)}%`;
}

// ================================================================
// DATAS
// ================================================================

function getMesAtual() {
    return new Date().getMonth() + 1;
}

function getAnoAtual() {
    return new Date().getFullYear();
}

function getNomeMes(mes) {
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    return meses[mes - 1] || mes;
}

function getNomeMesAbreviado(mes) {
    const meses = [
        'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ];
    return meses[mes - 1] || mes;
}

function getDataAtual() {
    const now = new Date();
    const options = { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' };
    return now.toLocaleDateString('pt-BR', options);
}

function getDataAtualCompleta() {
    const now = new Date();
    return now.toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ================================================================
// STATUS E BADGES
// ================================================================

function renderizarStatus(fase) {
    if (!fase) return '<span class="status-badge info">-</span>';
    
    const fases = {
        '0 a 90': 'success',
        '91 a 180': 'info',
        '181 a 360': 'warning',
        '361 a 720': 'warning',
        '721 a 1080': 'danger',
        '1081 a 1440': 'danger',
        '1441 a 1800': 'danger',
        '> 1800': 'danger',
        'Fora da fase': 'info'
    };
    const classe = fases[fase] || 'info';
    return `<span class="status-badge ${classe}">${fase}</span>`;
}

function getStatusClass(fase) {
    if (!fase) return 'info';
    const fases = {
        '0 a 90': 'success',
        '91 a 180': 'info',
        '181 a 360': 'warning',
        '361 a 720': 'warning',
        '721 a 1080': 'danger',
        '1081 a 1440': 'danger',
        '1441 a 1800': 'danger',
        '> 1800': 'danger',
        'Fora da fase': 'info'
    };
    return fases[fase] || 'info';
}

function getStatusLabel(fase) {
    if (!fase) return 'Indefinido';
    const labels = {
        '0 a 90': 'Em dia',
        '91 a 180': 'Atenção',
        '181 a 360': 'Atraso Moderado',
        '361 a 720': 'Atraso Grave',
        '721 a 1080': 'Atraso Crítico',
        '1081 a 1440': 'Atraso Extremo',
        '1441 a 1800': 'Atraso Máximo',
        '> 1800': 'Atraso Total',
        'Fora da fase': 'Fora da fase'
    };
    return labels[fase] || fase;
}

// ================================================================
// INICIAIS DO NOME
// ================================================================

function getIniciais(nome) {
    if (!nome) return 'U';
    const partes = nome.trim().split(' ');
    if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
    const iniciais = partes.map(p => p[0]).join('').substring(0, 2);
    return iniciais.toUpperCase();
}

// ================================================================
// CORES ALEATÓRIAS
// ================================================================

function getCorAleatoria() {
    const cores = [
        '#7e3d97', '#9b5bad', '#10B981', '#3498db', 
        '#f39c12', '#e74c3c', '#8e44ad', '#2ecc71',
        '#1abc9c', '#e67e22', '#e74c3c', '#3498db'
    ];
    return cores[Math.floor(Math.random() * cores.length)];
}

// ================================================================
// VALIDAÇÃO
// ================================================================

function isVazio(valor) {
    return valor === undefined || valor === null || valor === '';
}

function isNumero(valor) {
    return !isNaN(parseFloat(valor)) && isFinite(valor);
}

// ================================================================
// BARRA DE PROGRESSO (% Meta em células de tabela)
// ================================================================

function criarBarraProgresso(percentual, minWidth) {
    const perc = parseFloat(percentual) || 0;
    const corClasse = perc >= 100 ? 'green' : 'purple';
    const largura = minWidth || 110;
    return `
        <div class="table-progress-container" style="min-width:${largura}px;">
            <div class="table-progress-bar">
                <div class="table-progress-fill ${corClasse}" style="width: ${Math.min(perc, 100)}%;"></div>
            </div>
            <span class="table-progress-text" style="color: ${perc >= 100 ? 'var(--emerald)' : 'var(--purple-main)'};">${perc.toFixed(1)}%</span>
        </div>
    `;
}

// ================================================================
// EXPORTAR (para uso em outros arquivos)
// ================================================================

// Se estiver usando módulos ES6, descomente:
// export {
//     formatarMoeda,
//     formatarData,
//     formatarDataHora,
//     formatarDataCompleta,
//     formatarPercentual,
//     formatarPercentualComSinal,
//     getMesAtual,
//     getAnoAtual,
//     getNomeMes,
//     getNomeMesAbreviado,
//     getDataAtual,
//     getDataAtualCompleta,
//     renderizarStatus,
//     getStatusClass,
//     getStatusLabel,
//     getIniciais,
//     getCorAleatoria,
//     isVazio,
//     isNumero
// };