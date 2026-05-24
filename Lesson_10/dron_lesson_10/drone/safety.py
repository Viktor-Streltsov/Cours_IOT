def check_battery(tello):
    battery = tello.get_battery()

    print(f"Battery: {battery}")

    if battery < 20:
        raise Exception("Battery is low")
