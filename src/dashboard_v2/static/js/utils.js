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