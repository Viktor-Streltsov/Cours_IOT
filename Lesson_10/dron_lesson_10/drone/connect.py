from djitellopy import Tello


def connect_drone():
    print('Connecting to drone ...')

    tello = Tello()
    tello.connect()

    print('Connected to drone ...')

    return tello
