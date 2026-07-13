"""
SERVICES - Lógica de Negócio do Dashboard V2
============================================

Organização dos serviços:
- admin_service: Lógica do dashboard ADM
- operador_service: Lógica do dashboard do operador
- db_service: Acesso ao banco de dados (existente)
- analytics_service: Cálculos e indicadores (existente)
- email_service: Envio de emails (existente)
"""

from .admin_service import montar_dashboard_adm
from .operador_service import montar_dashboard_operador, montar_performance_operador

__all__ = [
    'montar_dashboard_adm',
    'montar_dashboard_operador',
    'montar_performance_operador'
]