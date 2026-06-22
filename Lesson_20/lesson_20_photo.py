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

print("Нажмите 'q' для выхода, 's' для скриншота")

while True:
    # Получение и обработка кадра
    frame = frame_read.frame
    if frame is None:
        continue

    # Изменение размера
    display = cv2.resize(frame, (640, 480))

    # Добавление информации
    cv2.putText(display, f"Battery: {tello.get_battery()}%", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Отображение
    cv2.imshow("Tello Video", display)

    # Обработка клавиш
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('s'):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        cv2.imwrite(f"tello_{timestamp}.jpg", display)
        print(f"Скриншот сохранён")

# Завершение
tello.streamoff()
cv2.destroyAllWindows()