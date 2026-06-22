from djitellopy import Tello
import cv2
import time
from datetime import datetime

# Подключение
tello = Tello()
tello.connect()
print(f"Батарея: {tello.get_battery()}%")

# Видеопоток
tello.streamon()
frame_read = tello.get_frame_read()
time.sleep(2)

# Настройка записи видео
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(f'tello_video_{datetime.now().strftime("%Y%m%d_%H%M%S")}.avi',
                      fourcc, 20.0, (640, 480))

print("Нажмите 'q' для выхода, 's' для скриншота, 'p' для паузы")

recording = True

while True:
    frame = frame_read.frame
    if frame is None:
        continue

    # Изменение размера
    display = cv2.resize(frame, (640, 480))

    # Информация на экране
    status = "REC" if recording else "PAUSE"
    color = (0, 255, 0) if recording else (0, 0, 255)
    cv2.putText(display, f"{status} | Battery: {tello.get_battery()}%",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Запись видео
    if recording:
        out.write(display)

    # Отображение
    cv2.imshow("Tello Video", display)

    # Обработка клавиш
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('s'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cv2.imwrite(f"tello_{timestamp}.jpg", display)
        print(f"Скриншот сохранён")
    elif key == ord('p'):
        recording = not recording
        print(f"Запись: {'Включена' if recording else 'Приостановлена'}")

# Завершение
out.release()
tello.streamoff()
cv2.destroyAllWindows()
print("Видео сохранено!")