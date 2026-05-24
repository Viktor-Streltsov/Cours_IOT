from drone.connect import connect_drone
from drone.movement import (
    takeoff_dron,
    land_drone,
    move_up_drone,
    move_down_drone
)
from drone.safety import check_battery
from missions.patrol import patrol_mission
from missions.square import fly_square

# Подключение
tello = connect_drone()

# Проверка батареи
check_battery(tello)

# Главное меню
while True:
    print("\n=== Drone Control Menu ====")
    print("1 - Take off")
    print("2 - Move Up")
    print("3 - Move Down")
    print("4 - Fly Square")
    print("5 - Fly Patrol")
    print("6 - Land")
    print("0 - Exit")

    try:
        command = int(input("Enter a command: "))

        if command == 1:
            takeoff_dron(tello)
        elif command == 2:
            move_up_drone(tello)
        elif command == 3:
            move_down_drone(tello)
        elif command == 4:
            fly_square(tello)
        elif command == 5:
            patrol_mission(tello)
        elif command == 6:
            land_drone(tello)
        elif command == 0:
            print("Exiting...")
            break
        else:
            print("Invalid command")

    except ValueError:
        print("Invalid command")

try:
    if tello.is_flying:
        tello.land()
except:
    pass

print("Drone missing completed!")
