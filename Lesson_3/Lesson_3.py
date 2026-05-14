# Второй запуск дрона DJI Tello
# Взлёт, простое движение и посадка

from djitellopy import Tello

# Создание объекта дрона
print('Create Tello object')
tello = Tello()

# Подключение к дрону
print("Connecting to Tello Drone")
tello.connect()

# Проверка батареи
battery_level = tello.get_battery()
print(f'Battery level: {battery_level}%')

# Проверка заряда перед полётом
if battery_level < 20:
    print('Battery is low, takeoff cancelled')
else:
    print('Take off')

    # Взлёт
    tello.takeoff()

    # Подъём вверх на 40 см
    print('Move up')
    tello.move_up(40)

    # Спуск вниз на 40 см
    print('Move down')
    tello.move_down(40)

    # Посадка
    print('Landing')
    tello.land()

print("Done")
