import os
import csv

def read_existing_articles(file_path):
    """
    Читает существующие статьи из CSV файла и возвращает их ссылки в виде множества.

    Аргументы:
        file_path (str): Путь к CSV файлу, содержащему данные об уже существующих статьях.

    Возвращает:
        set: Множество ссылок на статьи, уже существующие в файле.
    """
    existing_articles = set()
    if os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if "article_link" in row:
                    existing_articles.add(row["article_link"])

    return existing_articles