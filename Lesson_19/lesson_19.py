import cv2
import time
from djitellopy import Tello
from datetime import datetime

# Настройки
SAVE_WIDTH, SAVE_HEIGHT = 480, 360

# Подключение к дрону
tello = Tello()
tello.connect()
print(f"Батарея: {tello.get_battery()}%")

# Настройка видеопотока
tello.streamon()
frame_read = tello.get_frame_read()
time.sleep(2)

# Захват и обработка фото
frame = frame_read.frame
resized = cv2.resize(frame, (SAVE_WIDTH, SAVE_HEIGHT))

# Добавление информации
cv2.putText(resized, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# Сохранение
filename = f"tello_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
cv2.imwrite(filename, resized)
print(f"Фото сохранено: {filename}")

# Завершение
tello.streamoff()
tello.end()