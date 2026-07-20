"""
YOLOv8_Person_Detect_Follow.py

Дрон DJI Tello использует стандартную предобученную модель YOLOv8 (yolov8n.pt,
обучена на датасете COCO, 80 классов), находит на кадре человека (класс 'person')
и должен поворачиваться/лететь так, чтобы держать человека в центре кадра.
"""

import djitellopy
from ultralytics import YOLO
from ultralytics.engine.results import Results
import cv2
from djitellopy import Tello

GREEN = (0, 255, 0)
RED = (0, 0, 255)

# ИСПРАВЛЕНО: было 'YOLOv8n.pt' (с большими буквами), а загруженный файл называется
# 'yolov8n.pt' (маленькими буквами). На Windows это могло сработать случайно
# (там имена файлов нечувствительны к регистру), но на Linux/macOS привело бы
# к ошибке "файл не найден". Указываем имя файла ровно так, как он называется на диске.
model = YOLO('yolov8n.pt')

# --- Подключение к дрону ---
tello: Tello = djitellopy.Tello()
tello.connect()
tello.streamon()

print("Battery is " + str(tello.get_battery()))

# tello.takeoff()
# tello.move_up(40)

frame_read = tello.get_frame_read()

while True:
    cv2.waitKey(1)

    tello_video_image = frame_read.frame

    results: list[Results] = model(tello_video_image)
    boxes = results[0].boxes

    found_person = False

    for box in boxes:
        class_id = int(box.cls.item())
        label = model.names[class_id]  # ИСПРАВЛЕНО: индексация вместо pop() (см. пояснение ниже)

        if label != 'person':
            continue  # нас интересуют только люди, остальные классы (стул, машина и т.д.) пропускаем

        # Пояснение по багу с .pop():
        # model.names.pop(class_id) не просто читает имя класса, а УДАЛЯЕТ его из словаря model.names.
        # Если бы мы вызвали .pop() несколько раз для одного и того же class_id
        # (как это было в исходном коде для печати, подписи текста и т.д.),
        # второй вызов упал бы с KeyError, т.к. ключ уже был удалён первым вызовом.
        # Поэтому класс нужно прочитать один раз через model.names[class_id] и переиспользовать переменную.

        x1, y1, x2, y2 = box.xyxy.numpy()[0]
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        confidence = box.conf.item()

        cv2.putText(tello_video_image, f'{label} {round(confidence, 2)}%',
                    (int(x1), int(y1) - 6), cv2.FONT_ITALIC, 1, GREEN, 2)
        cv2.rectangle(tello_video_image, (int(x1), int(y1)), (int(x2), int(y2)), GREEN, 3)

        centerX = int(x1 + (abs(x1 - x2) / 2))
        centerY = int(y1 + (abs(y1 - y2) / 2))
        print('center =', centerX, centerY)
        cv2.circle(tello_video_image, (centerX, centerY), 15, RED, 5)

        # Три зоны по горизонтали кадра: лево / центр / право
        if centerX < 170:
            print('yaw -40')
            # tello.send_rc_control(0, 0, 0, -30)
        elif centerX > 450:
            print('yaw 430')
            # tello.send_rc_control(0, 0, 0, 30)
        else:
            print('forward 40')
            # tello.send_rc_control(0, 40, 0, 0)

        found_person = True
        break  # реагируем только на первого найденного человека в кадре

    if not found_person:
        # print('yaw +10')  # можно запустить сканирование поворотом, если человек не найден
        # tello.send_rc_control(0, 0, 0, 10)
        pass

    cv2.imshow("YOLOv8 Inference", tello_video_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.streamoff()
cv2.destroyAllWindows()
