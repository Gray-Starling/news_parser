async def async_fetch_html(session, url):
    """
    Асинхронно загружает HTML контент по указанному URL с использованием заданной сессии.

    Аргументы:
        session (aiohttp.ClientSession): Сессия для выполнения HTTP запросов.
        url (str): URL, по которому нужно выполнить запрос.

    Возвращает:
        str: HTML контент страницы, если запрос успешен.
        None: Если произошла ошибка при выполнении запроса или статус ответа не равен 200.

    Исключения:
        Если возникает ошибка при выполнении запроса, она выводится на печать.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    try:
        if "https://lenta.ru/" in url:
            async with session.get(url, headers={"Host": "lenta.ru"}) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    response.raise_for_status()
        elif "https://www.gazeta.ru/" in url:
            async with session.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    response.raise_for_status()
        else:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
