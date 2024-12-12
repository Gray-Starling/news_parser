from dotenv import load_dotenv
import os
from tools.logger import setup_logger

load_dotenv()

SERVER_PORT = os.getenv('SERVER_PORT')
GET_NEWS_DATA_API_PATH = os.getenv('GET_NEWS_DATA_API_PATH')

server_logger = setup_logger("server", "server")
scrapper_logger = setup_logger("scrapper", "scrapper")
rbk_logger = setup_logger("rbk", "src/rbk")
lenta_logger = setup_logger("lenta", "src/lenta")
ria_logger = setup_logger("ria", "src/ria")
gazeta_logger = setup_logger("gazeta", "src/gazeta")
