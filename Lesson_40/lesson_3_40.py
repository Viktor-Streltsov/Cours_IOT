"""
YOLOv8_Mask_NoMak_Face_Follow.py

Дрон DJI Tello ищет на кадре лицо и определяет, надета ли на человеке маска
(модель Mask_best_200_epoch.pt обучена на 2 классах: 'Mask Wearing' и 'No Mask').
Затем дрон должен поворачиваться/лететь так, чтобы держать найденный объект
примерно по центру кадра.

ВАЖНО (главное исправление в этом файле):
В исходном варианте использовалось `model.names.pop(box.cls.item())`.
Метод `.pop()` у словаря НЕ ТОЛЬКО возвращает значение, но и УДАЛЯЕТ его из словаря.
Так как в коде эта строка вызывалась несколько раз подряд для одного и того же
объекта (box), второй и третий вызов пытались достать уже удалённый ключ ->
программа падала с ошибкой KeyError.
Исправление: класс объекта нужно прочитать ОДИН раз через индексацию `model.names[...]`
(без удаления) и сохранить в переменную `label`, а дальше использовать эту переменную.
"""

import cv2
import djitellopy
from djitellopy import Tello
from ultralytics import YOLO
from ultralytics.engine.results import Results

# Цвета в формате BGR (так, как их использует OpenCV)
GREEN = (0, 255, 0)   # используем для класса "Mask Wearing" (маска надета - хорошо)
RED = (0, 0, 255)     # используем для класса "No Mask" (маски нет)

# Загружаем свою обученную модель (не стандартный yolov8n.pt, а дообученную под 2 класса)
model = YOLO('Mask_best_200_epoch.pt')

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

    # Прогоняем текущий кадр через модель YOLO. Получаем список результатов (по одному на кадр).
    results: list[Results] = model(tello_video_image)

    boxes = results[0].boxes  # все найденные на кадре объекты (рамки + класс + уверенность)

    # Флаг, нужен, чтобы понять, нашли ли мы хоть один интересующий нас объект в этом кадре
    found_target = False

    for box in boxes:
        class_id = int(box.cls.item())
        label = model.names[class_id]  # ИСПРАВЛЕНО: индексация вместо pop() - словарь не портится
        confidence = box.conf.item()

        # Координаты рамки объекта: x1,y1 - левый верхний угол, x2,y2 - правый нижний угол
        x1, y1, x2, y2 = box.xyxy.numpy()[0]
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)

        if label == 'Mask Wearing':
            color = GREEN
        elif label == 'No Mask':
            color = RED
        else:
            # Если модель вернула класс, который нас не интересует - пропускаем этот box
            continue

        # Подписываем и рисуем рамку вокруг найденного лица/маски
        cv2.putText(tello_video_image, f'{label} {round(confidence, 2)}%',
                    (int(x1), int(y1) - 6), cv2.FONT_ITALIC, 1, color, 2)
        cv2.rectangle(tello_video_image, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)

        # Вычисляем центр найденного объекта - именно на него будет ориентироваться дрон
        centerX = int(x1 + (abs(x1 - x2) / 2))
        centerY = int(y1 + (abs(y1 - y2) / 2))
        print('center =', centerX, centerY)
        cv2.circle(tello_video_image, (centerX, centerY), 15, RED, 5)

        # Простая логика управления по горизонтали (yaw), по трём зонам кадра:
        # левая треть -> поворот влево, правая треть -> поворот вправо, середина -> лететь вперёд
        if centerX < 170:
            print('yaw -40')
            # tello.send_rc_control(0, 0, 0, -30)
        elif centerX > 450:
            print('yaw 430')
            # tello.send_rc_control(0, 0, 0, 30)
        else:
            print('forward 40')
            # tello.send_rc_control(0, 40, 0, 0)

        found_target = True
        break  # реагируем только на первый найденный объект в кадре (самый простой вариант)

    if not found_target:
        # Если ни одно лицо/маска не найдены - можно, например, запустить сканирование поворотом
        # print('yaw +10')
        # tello.send_rc_control(0, 0, 0, 10)
        pass

    cv2.imshow("YOLOv8 Inference", tello_video_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.streamoff()
cv2.destroyAllWindows()
