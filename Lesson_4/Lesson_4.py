# Третий запуск дрона DJI Tello
# Взлёт и простое движение (влево и вправо)

from djitellopy import Tello

# Создание объекта дрона
print("Create Tello object")
tello = Tello()

# Подключение к дрону
print("Connecting to Tello Drone")
tello.connect()

# Проверка батареи
battery_level = tello.get_battery()
print(f"Battery: {battery_level}%")

# Проверка заряда перед взлётом
if battery_level < 20:
    print("Battery too low. Takeoff cancelled.")
else:
    # Взлёт
    print("Take off")
    tello.takeoff()

    # Движение влево
    print("Move left")
    tello.move_left(40)

    # Движение вправо
    print("Move right")
    tello.move_right(40)

    # Посадка
    print("Landing")
    tello.land()

print("Done")
