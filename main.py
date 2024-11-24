import pandas as pd
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import argparse

IMAGE_FOLDER = 'images/'

def get_year_ending(years_difference):
    """Определяет правильное окончание для количества лет."""
    ending_data = str(years_difference)
    ending = int(ending_data[-1])
    if ending == 0 or (5 <= ending <= 9):
        return 'лет'
    elif ending == 1:
        return 'год'
    else:
        return 'года'

def calculate_years_difference(start_year):
    """Вычисляет разницу в годах между текущим годом и заданным начальным годом."""
    current_year = datetime.now().year
    return current_year - start_year

def get_years_info(start_year):
    """Возвращает разницу в годах и правильное окончание для заданного начального года."""
    years_difference = calculate_years_difference(start_year)
    ending_year = get_year_ending(years_difference)
    return years_difference, ending_year

def parse_arguments():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(description='Веб-приложение для коллекции вин.')
    parser.add_argument('--data', type=str, default=os.getenv('DATA_FILE', 'wine.xlsx'),
                        help='Путь к файлу с данными (по умолчанию: wine.xlsx)')
    parser.add_argument('--config', type=str, default=os.getenv('CONFIG_FILE', 'config.json'),
                        help='Путь к конфигурационному файлу (по умолчанию: config.json)')
    return parser.parse_args()

def main():
    args = parse_arguments()

    excel_data_df = pd.read_excel(
        args.data,
        sheet_name='wine_al',
        usecols=['Категория', 'Название', 'Сорт', 'Цена', 'Картинка', 'Акция']
    )
    vine_category = excel_data_df.to_dict(orient='records')

    vine_product = defaultdict(list)

    for item in vine_category:
        item = {key: (value if pd.notna(value) else '') for key, value in item.items()}
        item['Картинка'] = os.path.join(IMAGE_FOLDER, item['Картинка'])
        category = item['Категория']
        vine_product[category].append(item)

    start_year = 1920
    years_difference, ending_year = get_years_info(start_year)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    rendered_page = template.render(
        text2=(f"Уже {years_difference} {ending_year} с вами"),
        vine_product_forhtml=vine_product
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()

