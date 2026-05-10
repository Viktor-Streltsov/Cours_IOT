# Модули и работа с файлами

# Можно в одну строву
# import datatime as d, time, sys, os

import datetime as d
import platform
import time
from math import sqrt as s

import my_module as my
from my_module import add_three_numbers as add

time.sleep(3)
print('Hello World!')  # Заморозит на 3 секунды

print(d.datetime.now().time())  # Вывдит время

print(platform.system())

print(s(25))

print(my.name)

print(add(3, 5, 8))
