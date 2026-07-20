"""
FaceTracking_Left_Right.py

Дрон DJI Tello следит за лицом человека и поворачивается ВЛЕВО/ВПРАВО (yaw),
чтобы держать лицо по центру кадра.

Идея:
- если лицо смещено вправо от центра кадра -> дрон поворачивается по часовой стрелке;
- если лицо смещено влево от центра кадра -> дрон поворачивается против часовой стрелки.
"""

from djitellopy import tello
import cv2

# --- Подключение к дрону ---
tello = tello.Tello()
tello.connect()

battery_level = tello.get_battery()
print(battery_level)

tello.streamon()


def adjust_tello_position(offset_x):
    """
    Поворачивает дрон влево/вправо в зависимости от смещения лица по оси X.

    :param offset_x: разница между x-координатой центра лица и x-координатой центра кадра.
                      offset_x < 0  -> лицо левее центра
                      offset_x > 0  -> лицо правее центра

    "Мёртвая зона" [-90, 90] нужна, чтобы дрон не дёргался туда-сюда,
    когда лицо и так уже почти в центре (небольшие колебания - это нормально).
    """
    if not -90 <= offset_x <= 90 and offset_x != 0:
        if offset_x < 0:
            # Лицо левее центра -> нужно повернуть камеру влево,
            # то есть повернуть дрон против часовой стрелки (yaw отрицательный)
            print('rotate_counter_clockwise')
            # tello.rotate_counter_clockwise(10)  # альтернатива - поворот на фикс. угол
            tello.send_rc_control(0, 0, 0, -15)

        elif offset_x > 0:
            # Лицо правее центра -> поворачиваем по часовой стрелке (yaw положительный)
            print('rotate_clockwise')
            # tello.rotate_clockwise(10)
            tello.send_rc_control(0, 0, 0, 15)


# ИСПРАВЛЕНО: раньше здесь был указан файл 'haarcascade_frontalface_alt2.xml',
# которого не было среди загруженных файлов - это вызвало бы ошибку при запуске.
# Используем тот же каскад, что и в других скриптах: 'haarcascade_frontalface_default.xml'.
# Если нужен именно alt2 - убедитесь, что этот .xml файл лежит рядом со скриптом.
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

frame_read = tello.get_frame_read()

tello.takeoff()
tello.move_up(30)

while True:
    frame = frame_read.frame

    cap = tello.get_video_capture()
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    print('height: ', height, '   width: ', width)

    # Центр кадра - точка, к которой мы стремимся привести центр лица
    center_x = int(width / 2)
    center_y = int(height / 2)

    cv2.circle(frame, (center_x, center_y), 10, (0, 255, 0), 6)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, minNeighbors=5)

    # Если лицо не найдено, центр лица считаем равным центру кадра -> offset_x будет 0,
    # и дрон просто не будет поворачиваться (это предохраняет от случайных резких движений).
    face_center_x = center_x
    face_center_y = center_y

    for face in faces:
        (x, y, w, h) = face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)

        face_center_x = x + int(w / 2)
        face_center_y = y + int(h / 2)

        cv2.circle(frame, (face_center_x, face_center_y), 10, (0, 0, 255), 6)

    # Вычисляем, насколько лицо смещено от центра кадра по горизонтали
    offset_x = face_center_x - center_x

    cv2.putText(frame, f'[{offset_x}]', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_8)
    adjust_tello_position(offset_x)

    cv2.imshow('Tello detection...', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        tello.land()
        break

tello.end()
cv2.destroyAllWindows()
