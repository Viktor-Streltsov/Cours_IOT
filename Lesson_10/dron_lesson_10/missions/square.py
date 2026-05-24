import time


def fly_square(tello):
    print("Starting square mission")

    for side in range(4):
        print(f"Side {side - 1}")

        tello.move_forward(50)
        time.sleep(1)

        tello.rotate_clockwise(90)
        time.sleep(1)

    print("Square mission completed")
