from pathlib import Path
import logging
import os
from src.conifg import LOG_DIR, PROJECT_ROOT





def setup_logging(log_level=logging.INFO):

    LOG_DIR.mkdir(exist_ok=True)

    log_filepath = LOG_DIR / "portfolio_analyzer.log"

    logger = logging.getLogger()
    logger.setLevel(log_level)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    print(f"Writing logs to: {log_filepath}")

    file_handler = logging.FileHandler(log_filepath)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging infrastructure successfully initialized.")
    return logger