import time
import threading
import asyncio
import os
from flask import Flask, send_file
from scrapper import main as scrapper_main
from config import server_logger, SERVER_PORT, GET_NEWS_DATA_API_PATH

app = Flask(__name__)
PORT = SERVER_PORT
API_PATH = GET_NEWS_DATA_API_PATH

def human_size(size):
    if size < 1e+9:
        return f"{size / 1e+6} МБ"
    else:
        return f"{size / 1e+9} ГБ"

def run_scrapper_periodically():
   
    while True:
        try: 
            server_logger.info("News scrapper is running")
            print("News scrapper is running")
            asyncio.run(scrapper_main())
            server_logger.info("News scrapper finished")
            print("News scrapper finished")
            file_path = "./data/news_data.csv"
            file_size = os.path.getsize(file_path)
            formatted_size = human_size(file_size)
            server_logger.info(f"Размер файла: {formatted_size}")
            print(f"Размер файла: {formatted_size}")
        except Exception as e:
            server_logger.error(f"Error running scrapper: {e}")
        server_logger.info("Sleeping for 10 minutes. \n")
        time.sleep(600)

@app.route(API_PATH)
def index():
    file_path = "./data/news_data.csv"
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    scrapper_thread = threading.Thread(target=run_scrapper_periodically)
    scrapper_thread.daemon = True
    scrapper_thread.start()

    app.run(port=PORT)