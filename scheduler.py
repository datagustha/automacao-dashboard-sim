"""
scheduler.py - Agendador Autonomo

Este arquivo é o ponto de entrada do sistema de agendamento.
Ele fica rodando indefinidamente na VPS e chama o main.py
automaticamente todos os dias nos horários definidos.

Como rodar:
    python scheduler.py

Para parar:
    Ctrl+C
"""

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────

import logging
# logging: biblioteca padrão do Python para registrar mensagens
# no terminal e em arquivos de log. Usamos para saber o que
# tá acontecendo sem precisar ficar olhando o terminal.

from apscheduler.schedulers.blocking import BlockingScheduler
# BlockingScheduler: o tipo de scheduler que "trava" o programa
# principal e fica rodando para sempre, dormindo entre execuções.
# Ideal para scripts que rodam em background numa VPS.
# Alternativa seria o BackgroundScheduler, mas ele precisaria
# de outro loop principal pra manter o programa vivo.

from apscheduler.triggers.cron import CronTrigger
# CronTrigger: define QUANDO o job vai rodar, no estilo cron.
# Permite especificar hora, minuto, dia da semana, etc.
# É mais poderoso que o schedule simples porque suporta
# timezone nativa e não desperdiça CPU entre execuções.

from src.main import main
# Importa a função main() do seu main.py que fica na raiz
# do projeto. É ela que orquestra todo o fluxo:
# scraping → processamento → banco de dados.


# ─────────────────────────────────────────────
# CONFIGURAÇÃO DE LOG
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    # INFO: mostra mensagens informativas, avisos e erros.
    # Se quiser mais detalhes use logging.DEBUG.
    # Se quiser menos use logging.WARNING.

    format="%(asctime)s [%(levelname)s] %(message)s",
    # Formato de cada linha do log:
    # %(asctime)s   → data e hora ex: 2026-04-29 08:30:00,123
    # %(levelname)s → nível ex: INFO, WARNING, ERROR
    # %(message)s   → a mensagem em si

    handlers=[
        logging.FileHandler("scheduler.log", encoding="utf-8"),
        # FileHandler: salva o log num arquivo chamado scheduler.log
        # na mesma pasta do script. encoding="utf-8" evita erro
        # com caracteres especiais no Windows.

        logging.StreamHandler()
        # StreamHandler: também mostra o log no terminal em tempo real.
        # Assim você vê o que tá acontecendo tanto no arquivo quanto
        # na tela.
    ]
)

# Cria o logger com o nome deste módulo (__name__ = "scheduler")
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# FUNÇÃO JOB — O QUE RODA EM CADA EXECUÇÃO
# ─────────────────────────────────────────────

def job():
    """
    Função chamada pelo scheduler nos horários definidos.
    Ela chama o main() e registra no log se deu certo ou errado.
    O try/except garante que se der erro numa execução,
    o scheduler continua vivo e tenta de novo no próximo horário.
    """
    log.info("Iniciando execucao agendada...")
    try:
        main()
        # Chama o fluxo completo: scraping → processamento → banco
        log.info("Execucao finalizada com sucesso!")

    except Exception as e:
        log.error(f"Erro durante execucao: {e}", exc_info=True)
        # exc_info=True faz o log registrar o traceback completo
        # do erro, facilitando muito o debug quando algo der errado.


# ─────────────────────────────────────────────
# PONTO DE ENTRADA — INICIA O SCHEDULER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # O bloco if __name__ == "__main__" garante que o scheduler
    # só inicia quando você roda este arquivo diretamente.
    # Se outro arquivo importar este módulo, o scheduler
    # não inicia sozinho.

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    # Cria o scheduler com timezone de Brasília.
    # Isso garante que os horários batem com o horário brasileiro
    # independente de onde a VPS estiver hospedada.

    # scheduler.add_job(job, CronTrigger(hour="8,11,16", minute=0))
    # Em vez de 8, 11, 16
    schedule.add_job(job, 'cron', hour=11, minute=40)  # Vai rodar 11:40
    # Registra o job para rodar às 8h00, 11h00 e 16h00 todo dia.
    # hour="8,11,16" → vírgula separa múltiplos horários
    # minute=0       → no minuto zero de cada hora
    # Para testar a cada 2 minutos usaríamos:
    # CronTrigger(minute="*/2")

    log.info("Scheduler rodando - 8h, 11h e 16h (Brasilia)")

    try:
        scheduler.start()
        # Inicia o scheduler — aqui o programa "trava" e fica
        # rodando para sempre, dormindo entre as execuções.
        # Não consome CPU enquanto dorme, só acorda na hora certa.

    except KeyboardInterrupt:
        log.info("Encerrado pelo usuario.")
        # Captura o Ctrl+C e encerra limpo ao invés de
        # mostrar um erro feio no terminal.