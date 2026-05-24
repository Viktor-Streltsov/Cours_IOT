import time

from djitellopy import Tello


def fly_pattern():
    tello = Tello()

    try:
        print("Connecting to Tello...")
        tello.connect()

        print(f"Battery: {tello.get_battery()}%")

        tello.takeoff()
        time.sleep(2)

        d = 50
        speed = 20

        print("Up")
        tello.go_xyz_speed(0, 0, d, speed)
        time.sleep(2)

        print("Diagonals 1")
        tello.go_xyz_speed(0, 0, -d, speed)
        time.sleep(2)

        print("Up again")
        tello.go_xyz_speed(0, 0, d, speed)
        time.sleep(2)

        print("Diagonals 2")
        tello.go_xyz_speed(0, -d, -d, speed)
        time.sleep(2)

        print("Finish position")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        try:
            tello.land()
        except:
            pass

        print("Mission completed")
