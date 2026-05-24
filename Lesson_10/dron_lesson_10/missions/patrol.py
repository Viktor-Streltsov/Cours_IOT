import time


def patrol_mission(tello, rounds=2):
    # Потрулирование по квадратному маршруту

    print("Start patrol mission")

    for rounds_number in range(rounds):
        print(f"Parol round {rounds_number + 1}")

        for side in range(4):
            print(f"Side {side + 1}")

            # Полет вперед
            tello.move_forward(100)
            time.sleep(1)

            # Поворот на право
            tello.rotate_clockwise(90)
            time.sleep(1)

    print("End patrol mission")
