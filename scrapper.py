import asyncio
import aiohttp
from aiohttp import ClientSession
import os
import csv
from config import scrapper_logger
from news_scrappers.rbk import async_rbk_news_scrapper
from news_scrappers.lenta import async_lenta_news_scrapper
from news_scrappers.ria import async_ria_news_scrapper
from news_scrappers.gazeta import async_gazeta_news_scrapper
from tools.existing_articles import read_existing_articles

# Словарь, сопоставляющий источники новостей и соответствующие им асинхронные функции-скраперы
SCRAPPERS = {
    "RBK": async_rbk_news_scrapper,
    "Lenta": async_lenta_news_scrapper,
    "RIA": async_ria_news_scrapper,
    "Gazeta": async_gazeta_news_scrapper,
}


async def fetch_news(session: ClientSession, scrapper_name: str, scrapper_function):
    """
    Асинхронно получает новостные статьи из указанной функции-скрапера новостей.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        scrapper_name (str): Название скрапера новостей.
        scrapper_function: Асинхронная функция, которая выполняет скрапинг новостей для определенного источника.

    Returns:
        list: Список словарей, представляющих новостные статьи, полученные из скрапера.

    """
    try:
        news = await scrapper_function(session)
        scrapper_logger.info(
            f"-- Fetched {len(news)} articles from {scrapper_name}.")
        return news
    except Exception as e:
        scrapper_logger.error(f"-- Error fetching {scrapper_name} news: {e}")
        return []


def write_to_csv(file_path, total_news_list, existing_articles):
    """
    Записывает новостные статьи в CSV-файл, пропуская статьи, которые уже есть в множестве `existing_articles`.

    Args:
        file_path (str): Путь к CSV-файлу, в который будут записаны новостные статьи.
        total_news_list (list): Список словарей, представляющих все полученные новостные статьи.
        existing_articles (Set[str]): Множество, содержащее URL статей, которые уже были записаны.

    Raises:
        Exception: В случае ошибки при записи в CSV-файл.

    """
    file_exists = os.path.exists(file_path)

    try:
        with open(file_path, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            if not file_exists or os.path.getsize(file_path) == 0:
                writer.writerow([
                    "news_source_name",
                    "news_source_link",
                    "category_name",
                    "category_link",
                    "article_date",
                    "article_link",
                    "article_title",
                    "article_text",
                ])

            for article in total_news_list:
                if article["article_link"] not in existing_articles:
                    writer.writerow([
                        article.get("news_source_name", ""),
                        article.get("news_source_link", ""),
                        article.get("category_name", ""),
                        article.get("category_link", ""),
                        article.get("article_date", ""),
                        article.get("article_link", ""),
                        article.get("article_title", ""),
                        article.get("article_text", ""),
                    ])
                    existing_articles.add(article["article_link"])
    except Exception as e:
        scrapper_logger.error(f"Error writing to CSV file: {e}")


async def main():
    """
    Асинхронная основная функция, координирующая процесс скрапинга новостей.
    Получает новостные статьи из нескольких источников, записывает их в CSV-файл и обрабатывает исключения.

    Raises:
        Exception: В случае неожиданной ошибки в процессе скрапинга новостей.

    """
    total_news_list = []
    existing_articles = set()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')  # формируем путь к папке 'data'

    if not os.path.exists(data_dir):  # проверяем существование папки
        os.makedirs(data_dir)  # создаем папку, если она не существует

    file_path = os.path.join(data_dir, 'news_data.csv')
    # file_path = os.path.join(script_dir, "./data/news_data.csv")
    existing_articles = read_existing_articles(file_path)

    try:
        scrapper_logger.info("Starting the news scrapper.")
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_name, scrapper_function in SCRAPPERS.items():
                tasks.append(fetch_news(
                    session, source_name, scrapper_function))

            news_results = await asyncio.gather(*tasks)

            for news in news_results:
                total_news_list.extend(news)

        write_to_csv(file_path, total_news_list, existing_articles)

        scrapper_logger.info("News scrapper finished.")

    except Exception as e:
        scrapper_logger.error(e)
