# Управление дроном Tello через консоль
from djitellopy import Tello

# Создаем объект дрона
tello = Tello()

try:
    # Подключение к дрону
    print("Connecting to Tello...")
    tello.connect()

    # Проверям батарею
    battery = tello.get_battery()
    print("Battery level:", battery)

    # Мимальный безопасный заряд
    if battery < 20:
        print("Battery is low")
        exit()

    print("\n=== Drone Control Menu ====")
    print("1 - Take off")
    print("2 - Move Up")
    print("3 - Move Down")
    print("4 - Land")
    print("0 - Exit")

    flying = False

    while True:
        try:
            command = int(input("\n Enter command: "))

            # Взлет
            if command == 1:
                if not flying:
                    print("Takin off...")
                    tello.takeoff()
                    flying = True
                else:
                    print("Drone is already flying")

            elif command == 2:
                if flying:
                    print("Moving up...")
                    tello.move_up(30)
                else:
                    print("Drone must take off first")

            # Опуститься вниз
            elif command == 3:
                if flying:
                    print("Moving down...")
                    tello.move_down(30)
                else:
                    print("Drone must take off first")

            elif command == 4:
                if flying:
                    print("Landing...")
                    tello.land()
                    flying = False
                else:
                    print("Drone is already on the ground")

            elif command == 0:
                print("Exiting...")
                break

            else:
                print("Invalid command")

        except ValueError:
            print("Please enter a number")

except Exception as error:
    print(f"Error: {error}")

finally:
    # Гарантированная посадка
    try:
        if tello.is_flying:
            print("Emergency landing...")
            tello.land()
    except:
        pass

    print("Drone mission completed!")
