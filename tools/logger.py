import os
import logging
from datetime import datetime

def setup_logger(logger_name, path_name):
    """
    Настраивает логгер с указанным именем.

    Создает директорию для логов, если она не существует, и настраивает логгер
    для записи логов в файл с именем, включающим текущую дату.

    Args:
        logger_name (str): Имя логгера.

    Returns:
        logging.Logger: Настроенный логгер.
    """
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs" if path_name == "_" else f"../logs/{path_name}"))

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    current_time = datetime.now()

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    log_file_path = os.path.join(logs_dir, f"{logger_name}_{current_time.strftime('%Y_%m')}.log")
    handler = logging.FileHandler(log_file_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    return logger