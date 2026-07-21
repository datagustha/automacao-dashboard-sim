# -*- coding: utf-8 -*-
"""
OPERADOR ROUTES - APIs do Operador
===================================
Gerencia os endpoints das APIs de operador, retornando dados de faturamento, metas,
pagamentos, performance, TMA e listagem de operadores, todos protegidos por controle de sessão.
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime
import json
import pathlib


def _similaridade_nomes(nome_a: str, nome_b: str) -> float:
    """Calcula similaridade entre dois nomes por sobreposição de palavras relevantes.
    Ignora artigos/preposições. Retorna score 0.0–1.0.
    Mesma lógica do ponto_scraper_service para garantir consistência no lookup do cache.
    """
    stop = {'da', 'de', 'do', 'das', 'dos', 'e', 'a', 'o', 'em', 'por', 'para'}

    def _palavras(nome: str) -> set:
        return {w for w in nome.strip().lower().split() if w not in stop and len(w) > 1}

    pa = _palavras(nome_a)
    pb = _palavras(nome_b)
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / max(len(pa), len(pb))

# Importações de persistência e serviços
from src.services.db_service import Buscar_login
from src.services.db_service import (
    Buscar_pagamento_semear,
    Buscar_pagamento_agoracred,
    buscar_metas_semear,
    buscar_metas_agoracred,
    buscar_todos_operadores_por_banco,
    buscar_tma_operador
)
from src.dashboard_new.services.operador_service import montar_dashboard_operador, montar_performance_operador

operador_bp = Blueprint('operador', __name__, url_prefix='/api')


@operador_bp.route('/operador/<login>')
def api_operador(login):
    """Retorna dados do operador pelo login."""
    print(f"[API] GET /api/operador/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if operador:
            return jsonify({'success': True, 'data': operador})
        else:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/resumo/<login>')
def api_resumo(login):
    """Retorna o resumo completo do dashboard para o operador."""
    print(f"[API] GET /api/resumo/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        # Filtros de data e faixa
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        faixa = request.args.get('faixa', 'todas')
        data_inicio = request.args.get('data_inicio', None)
        data_fim = request.args.get('data_fim', None)
        
        resultado = montar_dashboard_operador(operador, ano, mes, faixa=faixa, data_inicio=data_inicio, data_fim=data_fim)

        
        if resultado:
            return jsonify({'success': True, 'data': resultado})
        else:
            return jsonify({'success': False, 'message': 'Erro ao montar dashboard'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/pagamentos/<login>')
def api_pagamentos(login):
    """Retorna os pagamentos do operador."""
    print(f"[API] GET /api/pagamentos/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        banco = operador.get('banco', 'SEMEAR')
        
        # Busca pagamentos de acordo com o banco atribuído
        if banco == 'SEMEAR':
            pagamentos = Buscar_pagamento_semear(operador)
        elif banco == 'AGORACRED':
            pagamentos = Buscar_pagamento_agoracred(operador)
        else:
            pagamentos = Buscar_pagamento_semear(operador)
            if not pagamentos:
                pagamentos = Buscar_pagamento_agoracred(operador)
        
        # Converte em dicionário caso retorne objetos
        if pagamentos and not isinstance(pagamentos[0], dict):
            pagamentos = [p.__dict__ for p in pagamentos]
        
        return jsonify({
            'success': True,
            'data': pagamentos or [],
            'total': len(pagamentos or [])
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/metas/<login>')
def api_metas(login):
    """Retorna as metas do operador."""
    print(f"[API] GET /api/metas/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        banco = operador.get('banco', 'SEMEAR')
        
        # Busca metas de acordo com o banco atribuído
        if banco == 'SEMEAR':
            metas = buscar_metas_semear(operador)
        elif banco == 'AGORACRED':
            metas = buscar_metas_agoracred(operador)
        else:
            metas = buscar_metas_semear(operador)
            if not metas:
                metas = buscar_metas_agoracred(operador)
        
        return jsonify({
            'success': True,
            'data': metas or []
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/performance/<login>')
def api_performance(login):
    """Retorna a performance do operador."""
    print(f"[API] GET /api/performance/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        resultado = montar_performance_operador(operador, ano, mes)
        
        if resultado:
            return jsonify({'success': True, 'data': resultado})
        else:
            return jsonify({'success': False, 'message': 'Erro ao montar performance'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/tma/<login>')
def api_tma(login):
    """Retorna os dados de TMA do operador."""
    print(f"[API] GET /api/tma/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        banco = operador.get('banco', 'SEMEAR')
        tma = buscar_tma_operador(login, banco, ano, mes)
        
        return jsonify({
            'success': True,
            'data': tma or {}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/operadores')
def api_operadores():
    """Retorna lista de todos os operadores. Suporta ?somente_ativos=true para filtrar inativos."""
    print(f"[API] GET /api/operadores")

    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador') or {}
    banco_sessao = session.get('banco') or operador_sessao.get('banco')
    perfil_sessao = operador_sessao.get('perfil')

    if not session.get('login') and not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    # Apenas administradores podem listar todos os operadores do sistema
    is_admin = banco_sessao == 'ADM' or perfil_sessao == 'adm'
    if not is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    try:
        banco = request.args.get('banco', 'SEMEAR')
        # somente_ativos=true filtra operadores com atividade 'Inativo' / 'INATIVO'
        somente_ativos = request.args.get('somente_ativos', 'false').lower() == 'true'
        operadores = buscar_todos_operadores_por_banco(banco, somente_ativos=somente_ativos)

        return jsonify({
            'success': True,
            'data': operadores,
            'total': len(operadores)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/horarios/<login>')
@operador_bp.route('/horario/<login>')
def api_horarios_operador(login):
    """Retorna os dados de ponto eletrônico (horários D-1, banco de horas e histórico) para o operador."""
    print(f"[API] GET /api/horarios/{login}")
    
    # Verifica se o usuário está autenticado na sessão
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for Administrador
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        # Busca dados do cadastro do operador no MySQL (d_analista)
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
            
        # Calcula tempo de casa baseado na data de admissão
        tempo_casa = "Não informado"
        if operador.get('admissao'):
            try:
                dt_adm_str = str(operador['admissao'])
                if '/' in dt_adm_str:
                    dt_adm = datetime.strptime(dt_adm_str, "%d/%m/%Y")
                else:
                    dt_adm = datetime.strptime(dt_adm_str[:10], "%Y-%m-%d")
                dias = (datetime.now() - dt_adm).days
                anos = dias // 365
                meses = (dias % 365) // 30
                dias_rest = (dias % 365) % 30
                p = []
                if anos > 0:
                    p.append(f"{anos} ano{'s' if anos > 1 else ''}")
                if meses > 0:
                    p.append(f"{meses} {'meses' if meses > 1 else 'mês'}")
                if dias_rest > 0:
                    p.append(f"{dias_rest} dia{'s' if dias_rest > 1 else ''}")
                tempo_casa = ", ".join(p) if p else "Menos de 1 mês"
            except Exception:
                tempo_casa = "Não informado"
                
        # Leitura do cache de ponto (data/ponto_cache.json)
        pasta_data = pathlib.Path(__file__).parent.parent.parent.parent / "data"
        caminho_cache = pasta_data / "ponto_cache.json"
        
        dados_ponto_func = None
        data_atualizacao = None
        data_d1 = None
        
        if caminho_cache.exists():
            with open(caminho_cache, "r", encoding="utf-8") as f:
                cache_json = json.load(f)
                data_atualizacao = cache_json.get("ultima_atualizacao")
                data_d1 = cache_json.get("data_alvo_d1")
                funcionarios = cache_json.get("funcionarios", {})
                
                # Busca por login exato (chave minúscula)
                dados_ponto_func = funcionarios.get(login.lower()) or funcionarios.get(login)

                # Se não encontrou por login, tenta por similaridade de nome
                # (garante funcionamento mesmo quando o scraper indexou por chave temporária)
                if not dados_ponto_func:
                    nome_op = (operador.get("nome") or "").strip()
                    melhor_score = 0.0
                    melhor_match = None

                    for key, val in funcionarios.items():
                        nome_sec = (val.get("nome_secullum") or "").strip()
                        if nome_sec:
                            score = _similaridade_nomes(nome_op, nome_sec)
                            if score > melhor_score:
                                melhor_score = score
                                melhor_match = val

                    # Aceita match apenas se similaridade >= 60%
                    if melhor_score >= 0.60 and melhor_match:
                        dados_ponto_func = melhor_match
                        print(f"[API HORARIOS] Encontrado por similaridade: '{nome_op}' (score: {melhor_score:.0%})")

        # Se não houver dados no cache para o operador, monta estrutura com mensagem de aviso
        if not dados_ponto_func:
            dados_ponto_func = {
                "nome_secullum": operador.get("nome"),
                "login": login,
                "status": "nao_encontrado",
                "mensagem": f"Nome '{operador.get('nome')}' não encontrado na base de dados do Secullum RH",
                "card_d1": {
                    "data": data_d1 or "—",
                    "entrada1": "—",
                    "saida1": "—",
                    "entrada2": "—",
                    "saida2": "—",
                    "b_saldo": "—",
                    "b_total": "—"
                },
                "historico_mes": []
            }

        # Retorna o payload completo com dados de usuário + dados de ponto
        return jsonify({
            'success': True,
            'data': {
                'login': login,
                'nome': operador.get('nome'),
                'imagem': operador.get('imagem'),
                'banco': operador.get('banco'),
                'atividade': operador.get('atividade'),
                'admissao': operador.get('admissao'),
                'tempo_casa': tempo_casa,
                'ultima_atualizacao': data_atualizacao,
                'ponto': dados_ponto_func
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500