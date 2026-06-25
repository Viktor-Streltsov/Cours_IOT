""" Управление дроном Tello с клавиатуры через OpenCV"""

from djitellopy import Tello
import cv2
import time

# Подключение
tello = Tello()
tello.connect()
print(f"Батарея: {tello.get_battery()}%")

# Видеопоток
tello.streamon()
frame_read = tello.get_frame_read()
time.sleep(2)

print("\nУправление:")
print("t - взлёт | l - посадка | q - выход")
print("w/s/a/d - движение | arrows - повороты")

# ДОБАВЛЯЕМ ЗАДЕРЖКУ МЕЖДУ КОМАНДАМИ
last_command_time = 0
COMMAND_DELAY = 0.5  # Задержка 0.5 секунды между командами

while True:
    # Получение кадра
    frame = frame_read.frame
    if frame is not None:
        display = cv2.resize(frame, (640, 480))

        # Добавляем информацию на экран
        cv2.putText(display, f"Battery: {tello.get_battery()}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Tello Control", display)

    # Обработка клавиш
    key = cv2.waitKey(5) & 0xFF

    # ПРОВЕРКА ЗАДЕРЖКИ
    current_time = time.time()
    if current_time - last_command_time < COMMAND_DELAY:
        # Если прошло мало времени - пропускаем команду
        continue

    if key == ord('t'):
        tello.takeoff()
        print("Взлёт!")
        last_command_time = current_time

    elif key == ord('l'):
        tello.land()
        print("Посадка!")
        last_command_time = current_time

    elif key == ord('w'):
        tello.move_forward(50)
        print("Вперёд")
        last_command_time = current_time

    elif key == ord('s'):
        tello.move_back(50)
        print("Назад")
        last_command_time = current_time

    elif key == ord('a'):
        tello.move_left(50)
        print("Влево")
        last_command_time = current_time

    elif key == ord('d'):
        tello.move_right(50)
        print("Вправо")
        last_command_time = current_time

    elif key == ord('c'):
        tello.rotate_clockwise(360)
        print("Поворот 360°")
        last_command_time = current_time

    elif key == ord('q'):
        print("Выход...")
        tello.land()
        break

# Завершение
tello.streamoff()
cv2.destroyAllWindows()