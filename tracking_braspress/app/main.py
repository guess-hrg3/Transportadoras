from __future__ import annotations
import argparse
import os
from app.config.settings import Settings
from app.core.logger import get_logger
from app.use_cases.process_faturamento import ProcessFaturamento

def main():
    parser = argparse.ArgumentParser(description="Tracking Braspress - Inserção e Atualização de Ocorrências")
    parser.add_argument("command", choices=["insert", "update", "all"], help="Ação a executar")
    parser.add_argument("--since", dest="since", help="Data inicial (YYYYMMDD) para filtrar notas", required=False)

    args = parser.parse_args()

    # Permite override da data inicial via CLI sem mexer no .env
    if args.since:
        os.environ["FATURAMENTO_START_DATE"] = args.since

    settings = Settings()
    logger = get_logger("app.main")

    logger.info(f"Iniciando aplicativo com FATURAMENTO_START_DATE={settings.FATURAMENTO_START_DATE}")
    use_case = ProcessFaturamento(settings)

    if args.command == "insert":
        logger.info("Iniciando inserção de notas...")
        use_case.inserir_notas()
    elif args.command == "update":
        logger.info("Iniciando atualização via Braspress...")
        use_case.atualizar_notas()
    elif args.command == "all":
        logger.info("Iniciando inserção de notas...")
        use_case.inserir_notas()
        logger.info("Iniciando atualização via Braspress...")
        use_case.atualizar_notas()

    logger.info("Processo concluído.")

if __name__ == "__main__":
    main()