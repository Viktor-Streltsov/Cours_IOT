from time import sleep

from djitellopy import Tello

# Создание объекта дрона
tello = Tello()

# Подключение к дрону
print("Connection to Tello Complete")
tello.connect()

# Проверям заряд батареи
battery_level = tello.get_battery()
print(f"Battery level: {battery_level}")

if battery_level < 50:
    print("Tage off")
    tello.takeoff()

    # Даем дрону стабилизироваться
    sleep(3)

    # Пытаемся сделать флип вправо
    try:
        print("Flip Right")
        tello.flip_right()

    # Если произошла ошибка — выводим ее
    except Exception as e:
        print(f"Flip failed: {e}")

    # Посадка дрона
    print("Landing")
    tello.land()
