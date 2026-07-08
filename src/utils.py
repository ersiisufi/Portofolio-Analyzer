from pathlib import Path
import logging
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent

def setup_logging(log_level=logging.INFO):
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    log_filepath = log_dir / "portfolio_analyzer.log"

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