"""
YOLOv8_PreTraining_Classes_Detect.py

Самый простой пример: дрон Tello + предобученная модель YOLOv8 (yolov8n.pt).
Модель обучена на датасете COCO и умеет узнавать 80 стандартных классов объектов
(человек, стул, телефон, машина и т.д.). Скрипт просто рисует найденные объекты
на кадре и показывает результат - без управления полётом дрона.
Это хороший стартовый скрипт, чтобы студенты сначала увидели, что модель вообще
"видит" на видео с дрона, прежде чем переходить к скриптам с управлением (Follow-скрипты).
"""

from ultralytics import YOLO
from ultralytics.engine.results import Results
import cv2
from djitellopy import Tello

# --- Подключение к дрону ---
tello = Tello()
tello.connect()

tello.streamon()  # включаем видеопоток
frame_read = tello.get_frame_read()

# Загружаем стандартную предобученную модель (маленькая версия 'n' - nano, самая быстрая)
model = YOLO('yolov8n.pt')
# model = YOLO('Mask_best_200_epoch.pt')  # альтернатива - своя дообученная модель (2 класса: маска/без маски)

while True:
    cv2.waitKey(1)

    tello_video_image = frame_read.frame

    # Прогоняем кадр через модель. results[0] - результат для этого одного кадра.
    results: list[Results] = model(tello_video_image)

    # .plot() - встроенный метод ultralytics, который сам рисует рамки, подписи классов
    # и уверенность (confidence) поверх исходного кадра. Удобно для быстрой визуальной проверки.
    annotated_frame = results[0].plot()

    cv2.imshow("YOLOv8 Inference", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.streamoff()
cv2.destroyAllWindows()
