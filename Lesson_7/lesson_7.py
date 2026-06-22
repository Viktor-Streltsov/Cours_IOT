# Шестой запуск Tello

from djitellopy import Tello


def bounce_drone(heights):
    # Дрон поднимаеться на заданные высоты (вверх вниз)
    for height in heights:
        myTello.move_up(height)
        myTello.move_down(height)


myTello = Tello()

try:
    myTello.connect()  # Подключение
    myTello.takeoff()  # Взлет

    bounce_drone([30, 50, 50])  # Прыжки

    myTello.land()  # Посадка

except Exception as e:
    print(f'Error: {e}')
    myTello.land()
