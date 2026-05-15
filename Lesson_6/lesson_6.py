from djitellopy import Tello

# Создаём объект управления дроном
print('Create Tello object')
tello = Tello()

# Подключаемся к дрону по Wi-Fi
print('Connecting to Tello Drone')
tello.connect()

# Получаем и выводим уровень заряда батареи (в процентах)
battery_level = tello.get_battery()
print(f'Battery level: {battery_level}%')

# Проверяем заряд: летим только если батарея >= 20%
if battery_level >= 20:
    # Взлёт и зависание на высоте ~1 метр
    print("Take off")
    tello.takeoff()

    # Полет вперед на 140см
    print("Move Forward")
    tello.move_forward(140)

    # Поворот на 90° по часовой стрелке
    print("Rotate Clockwise 90°")
    tello.rotate_clockwise(180)

    # Полет вперед на 140см
    print("Move Forward")
    tello.move_forward(140)

    # Поворот на 90° против часовой стрелки (возврат в исходное положение)
    print("Rotate Counter Clockwise 90°")
    tello.rotate_counter_clockwise(180)

    # Посадка после выполнения манёвров
    print("Landing")
    tello.land()

else:
    # Если заряд низкий — не взлетаем во избежание падения дрона
    print("Battery too low to fly! Minimum 20% required.")
