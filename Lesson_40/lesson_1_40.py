"""
FaceTracking_Fwd_Bwd.py

Дрон DJI Tello следит за лицом человека и двигается ВПЕРЁД/НАЗАД,
чтобы держать лицо на примерно одинаковом расстоянии от камеры.

Идея простая:
- чем ближе лицо к камере — тем БОЛЬШЕ рамка вокруг него (площадь w*h растёт);
- чем дальше лицо — тем МЕНЬШЕ рамка.
Значит, по площади рамки лица можно понять, нужно лететь вперёд или назад.
"""

from djitellopy import tello
import cv2

# --- Подключение к дрону ---
tello = tello.Tello()
tello.connect()

battery_level = tello.get_battery()
print(battery_level)  # печатаем заряд батареи, чтобы убедиться, что дрон готов к полёту

tello.streamon()  # включаем видеопоток с камеры дрона


def adjust_tello_position(offset_z):
    """
    Двигает дрон вперёд или назад в зависимости от площади рамки лица.

    :param offset_z: площадь прямоугольника вокруг лица (w * h), в пикселях^2.
                      Если лицо не найдено, offset_z = 0.

    Логика:
    - Задаём "коридор" допустимых значений площади: [15000, 30000].
      Пока площадь внутри этого коридора — дрон стоит на месте (лицо на нужном расстоянии).
    - Если площадь МЕНЬШЕ 15000 — лицо слишком маленькое (человек далеко) -> летим ВПЕРЁД.
    - Если площадь БОЛЬШЕ 30000 — лицо слишком большое (человек близко) -> летим НАЗАД.
    - offset_z == 0 означает "лицо не найдено" — в этом случае никуда не летим.
    """
    if not 15000 <= offset_z <= 30000 and offset_z != 0:
        if offset_z < 15000:
            # tello.move_forward(20)  # альтернативный способ - двигаться на фикс. расстояние
            # send_rc_control(left_right, forward_backward, up_down, yaw)
            tello.send_rc_control(0, 15, 0, 0)  # летим вперёд с небольшой скоростью
            print('move_forward', offset_z)
        elif offset_z > 30000:
            tello.send_rc_control(0, -15, 0, 0)  # летим назад
            print('move_back', offset_z)


# Загружаем каскад Хаара для поиска лиц (готовая, заранее обученная модель OpenCV)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

frame_read = tello.get_frame_read()  # объект, из которого можно постоянно читать текущий кадр

tello.takeoff()      # взлёт
tello.move_up(30)    # немного поднимаемся, чтобы камера смотрела примерно на уровень лица

while True:
    frame = frame_read.frame  # берём текущий кадр с камеры дрона

    cap = tello.get_video_capture()
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    # Вычисляем центр кадра (геометрический центр изображения)
    center_x = int(width / 2)
    center_y = int(height / 2)

    # Рисуем зелёную точку в центре кадра — это "цель", к которой стремится лицо
    cv2.circle(frame, (center_x, center_y), 10, (0, 255, 0), 8)

    # Каскад Хаара работает с чёрно-белым (grayscale) изображением, поэтому переводим кадр
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Ищем лица на кадре.
    # scaleFactor - во сколько раз уменьшается изображение на каждом шаге поиска (чем меньше, тем точнее и медленнее)
    # minNeighbors - сколько соседних прямоугольников должно "согласиться", чтобы засчитать лицо (защита от ложных срабатываний)
    # minSize - минимальный размер лица в пикселях, которое мы ещё готовы обнаружить
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(20, 20)
    )

    # Значения по умолчанию на случай, если лицо не найдено на этом кадре
    z_area = 0
    face_center_x = center_x
    face_center_y = center_y

    for face in faces:
        (x, y, w, h) = face  # x,y - левый верхний угол рамки; w,h - ширина и высота рамки

        # Рисуем красный прямоугольник вокруг найденного лица
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)

        # ИСПРАВЛЕНО: раньше здесь были перепутаны w и h местами
        # (face_center_x считался через h, face_center_y - через w, что давало неверный центр)
        face_center_x = x + int(w / 2)
        face_center_y = y + int(h / 2)

        # Площадь рамки лица - главный показатель "расстояния" до человека
        z_area = w * h

        # Рисуем центр лица красной точкой
        cv2.circle(frame, (face_center_x, face_center_y), 10, (0, 0, 255), 8)
        cv2.putText(frame, f'[{z_area}]', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_8)

    # Дублирующая строка ниже нужна на случай, если лицо не найдено ни разу за цикл for
    # (тогда мы всё равно выведем текущее значение z_area = 0 на экран)
    cv2.putText(frame, f'[{z_area}]', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_8)

    # На основе площади рамки лица решаем, лететь вперёд, назад или оставаться на месте
    adjust_tello_position(z_area)

    cv2.imshow('Tello detection...', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        tello.land()  # аккуратная посадка при выходе
        break

# Останавливаем чтение видео и корректно завершаем работу с дроном
tello.end()
cv2.destroyAllWindows()
