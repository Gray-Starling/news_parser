from dotenv import load_dotenv
import os
from tools.logger import setup_logger

load_dotenv()

# ----- Настройка сервера -----

"""
-- SCRAPPER_SERVER_PORT -- 

Порт сервера установленный в .env файле каталога parser_server.
Используется если сервер запускается отдельно от всего проекта или если значение глобального порта не установлено.
"""
SCRAPPER_SERVER_PORT = os.getenv('SCRAPPER_SERVER_PORT')

"""
-- GLOBAL_SCRAPPER_SERVER_PORT -- 

Порт сервера установленный в .env файле глобального уровня.
Используется если сервер запускается совместно с другими проектами.
"""
GLOBAL_SCRAPPER_SERVER_PORT = os.getenv('GLOBAL_SCRAPPER_SERVER_PORT')

# Определение порта сервера
SERVER_PORT = GLOBAL_SCRAPPER_SERVER_PORT if GLOBAL_SCRAPPER_SERVER_PORT else SCRAPPER_SERVER_PORT

# ----- Настройка API  -----

"""
-- SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH -- 

Путь для получения данных новостей по API. Устанавливается в .env файле каталога parser_server.
"""
SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH = os.getenv('SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH')

"""
-- GLOBAL_SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH -- 

Путь для получения данных новостей по API.
Используется если сервер запускается совместно с другими проектами.
"""
GLOBAL_SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH = os.getenv('GLOBAL_SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH')

# Определение пути API
NEWS_DATA_API_PATH = GLOBAL_SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH if GLOBAL_SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH else SCRAPPER_SERVER_GET_NEWS_DATA_API_PATH



# Логгеры для различных компонентов
server_logger = setup_logger("server", "server")
scrapper_logger = setup_logger("scrapper", "scrapper")
rbk_logger = setup_logger("rbk", "src/rbk")
lenta_logger = setup_logger("lenta", "src/lenta")
ria_logger = setup_logger("ria", "src/ria")
gazeta_logger = setup_logger("gazeta", "src/gazeta")
