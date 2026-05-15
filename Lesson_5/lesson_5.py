# Четвертый запуск Tello

# Импортируем класс Tello из библиотеки djitellopy
from djitellopy import Tello


# Функция для проверки уровня батареи
def check_battery(drone):
    # Получаем заряд батареи дрона
    battery = drone.get_battery()

    # Выводим процент заряда
    print(f"Battery: {battery}")

    if battery < 20:
        return False
    else:
        return True


# Создаем объект дрона
tello = Tello()

# Подключение к дрону
print("Connect to Tello Drone")
tello.connect()

if check_battery(tello):
    # Взлет
    print("Teke off")
    tello.takeoff()

    # Полет вперед на 40см
    print("Move Forward")
    tello.move_forward(40)

    # Полет назад на 40см
    print("Move Backward")
    tello.move_back(40)

    # Полет вправо на 40см
    print("Move Right")
    tello.move_right(40)

    # Полет влево на 40см
    print("Move Left")
    tello.move_left(40)

    # Посадка
    print("Landing")
    tello.land()

else:

    # Если батарея разряжена
    print("Flight canceled")
