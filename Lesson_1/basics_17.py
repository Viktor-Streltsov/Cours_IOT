# =========================================
# ДЕКОРАТОРЫ В PYTHON
# =========================================

import webbrowser
from datetime import datetime


# =========================================
# ДЕКОРАТОР
# =========================================
# Декоратор добавляет дополнительную
# логику к функции без изменения самой функции

def validator(func):
    # wrapper перехватывает вызов функции
    def wrapper(url):

        print('--------------------------')
        print('Checking URL...')
        print('Time:', datetime.now())
        print('URL:', url)

        # Проверка ссылки
        if url.startswith("https://") or url.startswith("http://"):

            print('URL is valid ✅')

            # Вызываем оригинальную функцию
            func(url)

        else:
            print('Invalid URL ❌')
            print('The link must start with http:// or https://')

        print('--------------------------')

    return wrapper


# =========================================
# ОСНОВНАЯ ФУНКЦИЯ
# =========================================
# @validator подключает декоратор

@validator
def open_url(url):
    print('Opening browser...')
    webbrowser.open(url)


# =========================================
# ВЫЗОВ ФУНКЦИЙ
# =========================================

# Правильная ссылка
open_url("https://www.google.com")

# Неправильная ссылка
open_url("googlecom")


# =========================================
# БЕЗ ДЕКОРАТОРА
# =========================================

# Обычная функция с проверкой внутри

def open_url(url):
    # Проверка ссылки
    if url.startswith("https://") or url.startswith("http://"):
        print("Opening:", url)
    else:
        print("Invalid URL")


# Вызов функции
open_url("https://google.com")
open_url("google.com")
