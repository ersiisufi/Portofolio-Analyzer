import os
import logging

def setup_logging(log_dir: str = "../logs", log_level=logging.INFO):
    """
    Sets up system-wide logging to both console and a log file.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_filepath = os.path.join(log_dir, "portfolio_analyzer.log")
    
    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers if the logger is initialized multiple times in notebooks
    if logger.handlers:
        return logger

    # Log format: Timestamp [Level] Module: Message
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s: %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # 1. File Handler (Writes everything to disk)
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Stream Handler (Prints out to console/terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging infrastructure successfully initialized.")
    return logger