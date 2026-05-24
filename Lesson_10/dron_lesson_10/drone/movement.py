def takeoff_dron(tello):
    print("TakeOff")
    tello.takeoff()


def land_drone(tello):
    print("Landing")
    tello.land()


def move_up_drone(tello, distance=30):
    print(f"Move up {distance} cm")
    tello.move_up(distance)


def move_down_drone(tello, distance=30):
    print(f"Move down {distance} cm")
    tello.move_down(distance)
