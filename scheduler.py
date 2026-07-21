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

from src.services.ponto_scraper_service import executar_scraping_completo_ponto
# Importa a função principal do scraper de ponto eletrônico (Secullum RH).
# Ela roda o Selenium headless, coleta os horários de todos os funcionários
# do mês atual até D-1 e salva o cache em data/ponto_cache.json.


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
    print(">>>> PRINT DIRETO DO SCHEDULER <<<<", flush=True)
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
# JOB: SCRAPER DE PONTO ELETRÔNICO
# ─────────────────────────────────────────────

def job_ponto():
    """
    Função chamada diariamente para executar o scraper de ponto.
    Ela acessa o Secullum RH via Selenium em modo headless,
    coleta as marcações do mês atual de todos os funcionários
    até o dia D-1 (com regra de final de semana → sexta-feira)
    e atualiza o arquivo data/ponto_cache.json para leitura
    instantânea no Dashboard pelos operadores e pelo admin.
    """
    log.info("[PONTO] Iniciando scraper de ponto eletronico (Secullum RH)...")
    try:
        # Executa o scraping em modo headless (sem janela visível) — ideal para VPS
        sucesso = executar_scraping_completo_ponto(headless=True)

        # Registra o resultado no log
        if sucesso:
            log.info("[PONTO] Scraper de ponto finalizado com sucesso. Cache atualizado.")
        else:
            log.warning("[PONTO] Scraper de ponto encerrou com falha. Verifique o log acima.")

    except Exception as e:
        # O try/except garante que uma falha no scraper de ponto
        # não derruba o scheduler nem afeta os outros jobs
        log.error(f"[PONTO] Erro inesperado durante execucao do scraper de ponto: {e}", exc_info=True)


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

    # ── Job principal de pagamentos ──────────────────────────────
    scheduler.add_job(job, CronTrigger(hour="8,11,16", minute=0))
    # Roda às 8h00, 11h00 e 16h00 todo dia.
    # hour="8,11,16" → vírgula separa múltiplos horários
    # minute=0       → no minuto zero de cada hora

    # ── Job de ponto eletrônico (Secullum RH) ────────────────────
    # Roda 5x ao dia para manter o Dashboard sempre atualizado:
    #   08:30 → Primeira atualização da manhã (dados de D-1 prontos)
    #   10:00 → Atualização do meio da manhã
    #   14:00 → Após o almoço
    #   16:00 → Meio da tarde
    #   18:00 → Final do expediente
    scheduler.add_job(job_ponto, CronTrigger(hour="8", minute=30))
    scheduler.add_job(job_ponto, CronTrigger(hour="10,14,16,18", minute=0))

    log.info("Scheduler rodando:")
    log.info("  - Pagamentos: 8h, 11h e 16h (Brasilia)")
    log.info("  - Ponto Eletronico: 8h30, 10h, 14h, 16h e 18h (Brasilia)")

    try:
        scheduler.start()
        # Inicia o scheduler — aqui o programa "trava" e fica
        # rodando para sempre, dormindo entre as execuções.
        # Não consome CPU enquanto dorme, só acorda na hora certa.

    except KeyboardInterrupt:
        log.info("Encerrado pelo usuario.")
        # Captura o Ctrl+C e encerra limpo ao invés de
        # mostrar um erro feio no terminal.