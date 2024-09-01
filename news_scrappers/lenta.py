import os
import sys
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.fetch_html import async_fetch_html
from tools.pars_time_text import parse_time_text
from tools.existing_articles import read_existing_articles

from config import lenta_logger

async def parse_categories(session, url):
    """
    Асинхронно парсит категории новостей с указанного URL.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        url (str): URL сайта Lenta.ru для парсинга категорий.

    Returns:
        list: Список словарей, представляющих категории новостей, содержащий имя и ссылку на категорию.
    """
    lenta_logger.info("Parsing categories from %s", url)

    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        categories_ul = soup.find_all("ul", class_="menu__nav-list")

        categories = []

        for ul in categories_ul:
            for li in ul.find_all("li", class_="menu__nav-item"):
                a_tag = li.find("a", class_="menu__nav-link _is-extra")

                if a_tag:

                    if a_tag.get_text(strip=True) == "Главное":
                        continue

                    relative_link = a_tag["href"].lstrip("/")
                    category = {
                        "name": a_tag.get_text(strip=True),
                        "link": (
                            a_tag["href"]
                            if a_tag["href"].startswith("https")
                            else url + relative_link
                        ),
                    }
                    categories.append(category)
        lenta_logger.info("Found %d categories", len(categories))
        return categories

    except Exception as e:
        lenta_logger.error("Error parsing categories: %s", e)
    return []


async def parse_articles_in_category(session, url):
    """
    Асинхронно парсит статьи в указанной категории новостей.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        url (str): URL категории новостей.

    Returns:
        list: Список словарей, представляющих статьи, содержащий ссылки на статьи.
    """
    lenta_logger.info("-- Parsing articles in category %s", url)

    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/news_data.csv"))
    existing_articles = read_existing_articles(file_path)

    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        articles = []
        article_blocks = soup.find_all("div", class_="rubric-page__container")

        for block in article_blocks:
            first_block = block.find_all("div", class_="longgrid-feature-list")
            other_blocks = block.find_all("div", class_="longgrid-list")

            for element in first_block:
                links = element.find_all("a")
                for link in links:
                    relative_link = link["href"].lstrip("/")
                    article = {}
                    link_href = (
                            link["href"]
                            if link["href"].startswith("https")
                            else "https://lenta.ru/" + relative_link
                        )
                    if link_href not in existing_articles:
                        article["link"] = link_href
                        articles.append(article)
            for element in other_blocks:
                links = element.find_all("a")
                for link in links:
                    relative_link = link["href"].lstrip("/")
                    article = {}
                    link_href = (
                            link["href"]
                            if link["href"].startswith("https")
                            else "https://lenta.ru/" + relative_link
                        )
                    if link_href not in existing_articles:
                        article["link"] = link_href
                        articles.append(article)
        lenta_logger.info("-- Found %d articles in category %s", len(articles), url)
        return articles

    except Exception as e:
        lenta_logger.error("-- Error parsing articles in category %s: %s", url, e)
    return []


async def parse_articles(session, url):
    """
    Асинхронно парсит полную статью по указанному URL.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        url (str): URL статьи.

    Returns:
        dict: Словарь, представляющий статью, содержащий дату, заголовок и текст статьи.
    """
    lenta_logger.info("-- -- Parsing full article from %s", url)
    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        article_container = soup.find_all("div", class_="topic-page__container")
        article = {}
        for container in article_container:
            time_a_premium = container.find_all("a", class_="premium-header__time")
            time_a_regular = container.find_all("a", class_="topic-header__time")

            if time_a_premium:
                article["date"] = parse_time_text(
                    time_a_premium[0].get_text(strip=True),
                    "lenta"
                )
            if time_a_regular:
                article["date"] = parse_time_text(
                    time_a_regular[0].get_text(strip=True),
                    "lenta"
                )

            article["title"] = container.find("h1").get_text(separator=" ", strip=True)

            article_content_div = container.find_all("div", class_="topic-body")
            
            for incut in article_content_div[0].find_all("a", class_="topic-body__origin"):
                incut.decompose()
                
            for incut in article_content_div[0].find_all("div", class_="topic-body__title-image"):
                incut.decompose()
                
            for incut in article_content_div[0].find_all("div", class_="js-scroll-to-site-container"):
                incut.decompose()
                
            for incut in article_content_div[0].find_all("div", class_="box-inline-topic"):
                incut.decompose()
                
            for incut in article_content_div[0].find_all("div", class_="box-gallery"):
                incut.decompose()
                
            for incut in article_content_div[0].find_all("figure", class_="picture"):
                incut.decompose()
                
            article["text"] = article_content_div[0].get_text(separator=" ", strip=True)

            return article

    except Exception as e:
        lenta_logger.error("-- -- Error parsing article %s: %s", url, e)
    return {}


async def async_lenta_news_scrapper(session):
    """
    Асинхронно получает новости с сайта Lenta.ru.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.

    Returns:
        list: Список словарей, представляющих новостные статьи, содержащий информацию об источнике, категории, дате, ссылке, заголовке и тексте статьи.
    """
    main_url = "https://lenta.ru/"
    lenta_news = []

    categories = await parse_categories(session, main_url)

    for category in categories:
        articles = await parse_articles_in_category(session, category["link"])
        for element in articles:
            full_article = await parse_articles(session, element["link"])
            single_article = {
                "news_source_name": "lenta",
                "news_source_link": main_url,
                "category_name": category["name"],
                "category_link": category["link"],
                "article_date": full_article.get("date", ""),
                "article_link": element["link"],
                "article_title": full_article.get("title", ""),
                "article_text": full_article.get("text", ""),
            }
            lenta_news.append(single_article)
            lenta_logger.info("-- -- Added article: %s", single_article["article_link"])

    lenta_logger.info("Total articles scraped: %d", len(lenta_news))
    return lenta_news
