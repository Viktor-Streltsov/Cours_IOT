# Работа с менеджером With ... as  работа с файлами

# file = open('text.txt', 'r') # Ошибка такого файла нет
# file.read()
# file.close()

# try:
#     file = open('text.txt', 'r')
#     file.read()
# except FileNotFoundError:
#     print('File not found')
# finally:
#     file.close() # Невидна в этом блоке Ошибка

try:
    with open('text.txt', 'r', encoding='utf-8') as file:  # Самостоятельно закрывает фаил
        file.read()
except FileNotFoundError:
    print('File not found')
