# Первый запуск дрона DJI Tello
# Взлёт, ожидание и посадка

import time

from djitellopy import Tello

# Создаем объект дрона
print("Создание объекта Tello...")
tello = Tello()

# Подключаемся к дрону
print("Подключение к дрону...")
tello.connect()

# Проверяем заряд батареи
battery_level = tello.get_battery()
print(f"Уровень заряда: {battery_level}%")

# Проверка минимального заряда
if battery_level < 20:
    print("Слишком низкий заряд батареи!")
    print("Полет отменен.")
else:
    # Взлет
    print("Взлет...")
    tello.takeoff()

    # Небольшая задержка после взлета
    time.sleep(5)

    # Посадка
    print("Посадка...")
    tello.land()

    print("Полет завершен!")
