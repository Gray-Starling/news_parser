from config import ria_logger
from tools.existing_articles import read_existing_articles
from tools.pars_time_text import parse_time_text
from tools.fetch_html import async_fetch_html
import os
import sys
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


async def parse_categories(session, url):
    """
    Асинхронно парсит категории новостей с указанного URL.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        url (str): URL сайта RIA.ru для парсинга категорий.

    Returns:
        list: Список словарей, представляющих категории новостей, содержащий имя и ссылку на категорию.
    """
    ria_logger.info("Parsing categories from %s", url)
    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")
        categories = []

        title_divs = soup.find_all("div", class_="cell-extension__table")
        a_tags = title_divs[0].find_all("a")
        for a in a_tags:
            relative_link = a["href"].lstrip("/")
            category = {
                "name": a.get_text(strip=True),
                "link": (
                    a["href"] if a["href"].startswith(
                        "https") else url + relative_link
                ),
            }
            categories.append(category)
        ria_logger.info("Found %d categories", len(categories))
        return categories

    except Exception as e:
        ria_logger.error("Error parsing categories: %s", e)
    return []


async def parse_articles_in_category(session, url):
    """
    Асинхронно парсит статьи в указанной категории новостей.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        url (str): URL категории новостей.

    Returns:
        list: Список словарей, представляющих статьи, содержащий заголовки и ссылки на статьи.
    """
    ria_logger.info("-- Parsing articles in category %s", url)

    file_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../data/news_data.csv"))
    existing_articles = read_existing_articles(file_path)

    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        articles = []
        article_blocks = soup.find_all("div", class_="list-item__content")

        for block in article_blocks:

            a_tags = block.find_all("a", class_="list-item__title")

            for a in a_tags:
                if a["href"] not in existing_articles:
                    article = {}
                    article_title = a.get_text(strip=True)
                    relative_link = a["href"].lstrip("/")
                    link_href = (
                        a["href"]
                        if a["href"].startswith("https")
                        else url + relative_link
                    )
                    article["link"] = link_href
                    article["title"] = article_title
                    articles.append(article)

        ria_logger.info("-- Found %d articles in category %s",
                        len(articles), url)
        return articles

    except Exception as e:
        ria_logger.error(
            "-- Error parsing articles in category %s: %s", url, e)
    return []


async def parse_articles(session, url):
    """
    Асинхронно парсит полную статью по указанному URL.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        url (str): URL статьи.

    Returns:
        dict: Словарь, представляющий статью, содержащий дату и текст статьи.
    """
    ria_logger.info("-- -- Parsing full article from %s", url)
    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        article_date_block = soup.find_all("div", class_="article__info-date")

        article_date = article_date_block[0].find("a").get_text(strip=True)
        article_date = parse_time_text(article_date, "ria")

        content_div = soup.find_all("div", class_="article__body")

        all_text = []

        for div in content_div:
            blocks = div.find_all("div", class_="article__block")
            for block in blocks:
                if block.get("data-type") != "article" and block.get("data-type") != "photolenta":
                    all_text.append(block.get_text(separator=" ", strip=True))

        full_text = " ".join(all_text)

        article = {"date": article_date, "text": full_text}
        return article

    except Exception as e:
        ria_logger.error("-- -- Error parsing article %s: %s", url, e)
    return {}


async def async_ria_news_scrapper(session):
    """
    Асинхронно получает новости с сайта RIA.ru.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.

    Returns:
        list: Список словарей, представляющих новостные статьи, содержащий информацию об источнике, категории, дате, ссылке, заголовке и тексте статьи.
    """
    main_url = "https://ria.ru/"
    ria_news = []

    categories = await parse_categories(session, main_url)

    for category in categories:
        articles = await parse_articles_in_category(session, category["link"])

        for element in articles:
            full_article = await parse_articles(session, element["link"])
            single_article = {
                "news_source_name": "ria",
                "news_source_link": main_url,
                "category_name": category["name"],
                "category_link": category["link"],
                "article_date": full_article.get("date", ""),
                "article_link": element["link"],
                "article_title": element["title"],
                "article_text": full_article.get("text", ""),
            }

            ria_news.append(single_article)
            ria_logger.info("-- -- Added article: %s",
                            single_article["article_link"])

    ria_logger.info("Total articles scraped: %d", len(ria_news))
    return ria_news
