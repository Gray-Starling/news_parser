import pytz
from datetime import datetime
import locale


def parse_time_text(time_text, name):
    """
    Преобразует строку времени в формат ISO 8601 с учетом часового пояса Москвы.

    Аргументы:
        time_text (str): Строка с временем статьи.
        name (str): Название источника, чтобы определить формат строки времени.

    Возвращает:
        str: Время статьи в формате ISO 8601 с учетом часового пояса Москвы,
             или оригинальную строку времени в случае ошибки парсинга.

    Исключения:
        ValueError: Если строка времени не соответствует ожидаемому формату.
    """
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz)
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    try:

        if name == "ria":
            article_time = datetime.strptime(time_text, '%H:%M %d.%m.%Y')
        elif name == "lenta":
            article_time = datetime.strptime(time_text, '%H:%M, %d %B %Y')
        elif name == "rbk":
            if len(time_text) == 5 and ':' in time_text:
                article_time = datetime.strptime(time_text, '%H:%M').replace(
                    year=now.year, month=now.month, day=now.day)
            else:
                article_time = datetime.strptime(
                    time_text, '%d %b, %H:%M').replace(year=now.year)
        elif name == "gazeta":
            article_time = datetime.strptime(time_text, '%d %B %Y, %H:%M')
        else:
            return time_text

        article_time = moscow_tz.localize(article_time)
        return article_time.isoformat()
    except ValueError:
        return time_text
