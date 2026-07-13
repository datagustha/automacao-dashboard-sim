"""
ADMIN ROUTES - APIs do Dashboard ADM
=====================================
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime

from src.dashboard_v2.services.admin_service import montar_dashboard_adm

admin_bp = Blueprint('admin', __name__, url_prefix='/api')


@admin_bp.route('/resumo-adm')
def api_resumo_adm():
    """Retorna o resumo para o dashboard ADM."""
    print(f"[API] GET /api/resumo-adm")

    if not session.get('operador'):
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    try:
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        atividade = request.args.get('atividade', 'ATIVO')
        operador_filtro = request.args.get('operador', 'TODOS')
        contrato_filtro = request.args.get('contrato', '')
        faixa_filtro = request.args.get('faixa', 'todas')
        data_inicio = request.args.get('data_inicio', None)
        data_fim = request.args.get('data_fim', None)

        resultado = montar_dashboard_adm(
            ano=ano,
            mes=mes,
            atividade=atividade,
            operador_filtro=operador_filtro,
            contrato_filtro=contrato_filtro,
            faixa_filtro=faixa_filtro,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        return jsonify({
            'success': True,
            'data': resultado
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500