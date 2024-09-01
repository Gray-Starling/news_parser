from config import rbk_logger
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
        url (str): URL сайта RBC.ru для парсинга категорий.

    Returns:
        list: Список словарей, представляющих категории новостей, содержащий имя и ссылку на категорию.
    """
    rbk_logger.info("Parsing categories from %s", url)
    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        footer_title_divs = soup.find_all("div", class_="footer__title")
        for div in footer_title_divs:
            if div.get_text(strip=True) == "Рубрики":
                ul = div.find_next("ul")
                if ul:
                    categories = []
                    for li in ul.find_all("li"):
                        a = li.find("a")
                        if a:
                            if a.get_text(strip=True) == "Биографии":
                                continue
                            category = {
                                "name": a.get_text(strip=True),
                                "link": (
                                    a["href"]
                                    if a["href"].startswith("https")
                                    else url + a["href"]
                                ),
                            }
                            categories.append(category)
                    rbk_logger.info("Found %d categories", len(categories))
                    return categories
    except Exception as e:
        rbk_logger.error("Error parsing categories: %s", e)
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
    rbk_logger.info("-- Parsing articles in category %s", url)

    file_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../data/news_data.csv"))
    existing_articles = read_existing_articles(file_path)

    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        articles = []
        article_elements = soup.find_all(
            "div", class_="item__wrap l-col-center")

        for element in article_elements:
            article = {}
            time_span = element.find("span").get_text(strip=True)
            article_date = parse_time_text(time_span, "rbk")
            article_link = element.find("a")

            if article_link["href"] not in existing_articles:
                article["date"] = article_date
                article["link"] = article_link["href"]

                articles.append(article)
        rbk_logger.info("-- Found %d articles in category %s",
                        len(articles), url)
        return articles
    except Exception as e:
        rbk_logger.error(
            "-- Error parsing articles in category %s: %s", url, e)
    return []


async def parse_articles(session, url):
    """
    Асинхронно парсит полную статью по указанному URL.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.
        url (str): URL статьи.

    Returns:
        dict: Словарь, представляющий статью, содержащий заголовок и текст статьи.
    """
    rbk_logger.info("-- -- Parsing full article from %s", url)
    try:
        html = await async_fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        article_title = soup.find("h1").get_text(strip=True)
        article_text_div = soup.find_all(
            "div", class_="article__text article__text_free"
        )

        for incut in article_text_div[0].find_all("div", class_="article__main-image"):
            incut.decompose()

        for incut in article_text_div[0].find_all("div", class_="article__inline-item"):
            incut.decompose()

        for incut in article_text_div[0].find_all("span", class_="banner__container__color"):
            incut.decompose()

        for incut in article_text_div[0].find_all("div", class_="thg"):
            incut.decompose()

        for incut in article_text_div[0].find_all("div", class_="article__ticker"):
            incut.decompose()

        article_text = article_text_div[0].get_text(separator=" ", strip=True)

        article = {"title": article_title, "text": article_text}

        return article
    except Exception as e:
        rbk_logger.error("-- -- Error parsing article %s: %s", url, e)
    return {}


async def async_rbk_news_scrapper(session):
    """
    Асинхронно получает новости с сайта RBC.ru.

    Args:
        session (ClientSession): Объект ClientSession из aiohttp для выполнения HTTP-запросов.

    Returns:
        list: Список словарей, представляющих новостные статьи, содержащий информацию об источнике, категории, дате, ссылке, заголовке и тексте статьи.
    """
    main_url = "https://www.rbc.ru/"
    rbk_news = []

    categories = await parse_categories(session, main_url)

    for category in categories:
        articles = await parse_articles_in_category(session, category["link"])

        for element in articles:
            full_article = await parse_articles(session, element["link"])
            single_article = {
                "news_source_name": "rbk",
                "news_source_link": main_url,
                "category_name": category["name"],
                "category_link": category["link"],
                "article_date": element["date"],
                "article_link": element["link"],
                "article_title": full_article.get("title", ""),
                "article_text": full_article.get("text", ""),
            }

            rbk_news.append(single_article)
            rbk_logger.info("-- -- Added article: %s",
                            single_article["article_link"])

    rbk_logger.info("Total articles scraped: %d", len(rbk_news))
    return rbk_news
