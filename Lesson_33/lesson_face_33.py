import cv2
from djitellopy import Tello
from cvzone.FaceMeshModule import FaceMeshDetector
import cvzone
import time

# КОНФИГУРАЦИЯ
# Индексы ключевых точек лица
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 23
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374
MOUTH_LEFT = 61
MOUTH_RIGHT = 291
NOSE_TIP = 1
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263

# Пороги для мимики
BLINK_THRESHOLD = 3.0  # Расстояние между веками (меньше = закрыто)
MOUTH_THRESHOLD = 25  # Расстояние между углами рта

# Скорости движения
MOVE_SPEED = 20
ROTATE_SPEED = 20

# ПОДКЛЮЧЕНИЕ К ДРОНУ
print("=" * 50)
print("🚁 Tello Face Control (Мимика)")
print("=" * 50)

me = Tello()
me.connect(wait_for_state=False)
print(f"🔋 Батарея: {me.get_battery()}%")

me.streamon()
time.sleep(1)
frame_read = me.get_frame_read()

# ДЕТЕКТОР
detector = FaceMeshDetector(maxFaces=1)
fpsReader = cvzone.FPS()

# Состояния
is_flying = False
last_blink_time = 0
last_action_time = 0

print("\n УПРАВЛЕНИЕ МИМИКОЙ:")
print("Моргните = Движение вперёд")
print("Откройте рот = Движение назад")
print("Поверните голову влево = Поворот влево")
print("Поверните голову вправо = Поворот вправо")
print("Поднимите голову вверх = Движение вверх")
print(" ️Опустите голову вниз = Движение вниз")
print("[t] Взлёт [l] Посадка [q] Выход\n")


# ФУНКЦИИ УПРАВЛЕНИЯ
def process_face(face_points, img):
    """Обработка мимики и отправка команд дрону"""
    global is_flying, last_blink_time

    if not is_flying:
        return

    try:
        # 1. Получение координат ключевых точек
        # Глаза
        left_eye_top = face_points[LEFT_EYE_TOP]
        left_eye_bot = face_points[LEFT_EYE_BOTTOM]
        right_eye_top = face_points[RIGHT_EYE_TOP]
        right_eye_bot = face_points[RIGHT_EYE_BOTTOM]

        # Рот
        mouth_left = face_points[MOUTH_LEFT]
        mouth_right = face_points[MOUTH_RIGHT]

        # Нос
        nose = face_points[NOSE_TIP]

        # Внешние углы глаз (для поворота головы)
        left_eye_outer = face_points[LEFT_EYE_OUTER]
        right_eye_outer = face_points[RIGHT_EYE_OUTER]

        # 2. Вычисление расстояний
        # Расстояние между веками (моргание)
        left_eye_distance = ((left_eye_top[0] - left_eye_bot[0]) ** 2 +
                             (left_eye_top[1] - left_eye_bot[1]) ** 2) ** 0.5
        right_eye_distance = ((right_eye_top[0] - right_eye_bot[0]) ** 2 +
                              (right_eye_top[1] - right_eye_bot[1]) ** 2) ** 0.5
        avg_eye_distance = (left_eye_distance + right_eye_distance) / 2

        # Расстояние между углами рта
        mouth_distance = ((mouth_left[0] - mouth_right[0]) ** 2 +
                          (mouth_left[1] - mouth_right[1]) ** 2) ** 0.5

        # Наклон головы (горизонтальный)
        head_tilt = nose[0] - (left_eye_outer[0] + right_eye_outer[0]) / 2

        # Наклон головы (вертикальный)
        head_nod = nose[1] - (left_eye_outer[1] + right_eye_outer[1]) / 2

        # 3. Действия по мимике
        current_time = time.time()

        # Моргание (движение вперёд)
        if avg_eye_distance < BLINK_THRESHOLD:
            if current_time - last_blink_time > 1.0:  # Защита от случайных морганий
                print("Моргание -> Вперёд!")
                me.move_forward(MOVE_SPEED)
                last_blink_time = current_time
                cv2.putText(img, "FORWARD", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Открытый рот (движение назад)
        elif mouth_distance > MOUTH_THRESHOLD:
            if current_time - last_action_time > 0.5:
                print("👄 Рот открыт -> Назад!")
                me.move_backward(MOVE_SPEED)
                last_action_time = current_time
                cv2.putText(img, "BACKWARD", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Поворот головы влево
        elif head_tilt < -30:
            print("⬅️ Поворот головы влево")
            me.rotate_counter_clockwise(ROTATE_SPEED)
            cv2.putText(img, "ROTATE LEFT", (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Поворот головы вправо
        elif head_tilt > 30:
            print("➡️ Поворот головы вправо")
            me.rotate_clockwise(ROTATE_SPEED)
            cv2.putText(img, "ROTATE RIGHT", (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Наклон головы вверх (движение вверх)
        elif head_nod < -30:
            print("⬆️ Голова вверх")
            me.move_up(MOVE_SPEED)
            cv2.putText(img, "UP", (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Наклон головы вниз (движение вниз)
        elif head_nod > 30:
            print("⬇Голова вниз")
            me.move_down(MOVE_SPEED)
            cv2.putText(img, "DOWN", (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 4. Отображение параметров на экране
        cv2.putText(img, f"Eye: {avg_eye_distance:.1f}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"Mouth: {mouth_distance:.1f}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"Tilt: {head_tilt:.1f}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"Nod: {head_nod:.1f}", (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    except Exception as e:
        print(f"Ошибка обработки: {e}")


# ОСНОВНОЙ ЦИКЛ
try:
    while True:
        # Получение кадра
        img = frame_read.frame
        if img is None:
            continue

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Детекция лица
        img, faces = detector.findFaceMesh(img, draw=True)

        if faces:
            # Обработка мимики
            process_face(faces[0], img)
        else:
            cv2.putText(img, "No face detected", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Информация на экране
        cv2.putText(img, f"Flying: {is_flying}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"Battery: {me.get_battery()}%", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # FPS
        fps, img = fpsReader.update(img)

        # Отображение
        cv2.imshow("Tello Face Control", img)

        # Обработка клавиш
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Выход...")
            break
        elif key == ord('t'):
            if not is_flying:
                print("Взлёт!")
                me.takeoff()
                is_flying = True
            else:
                print("Дрон уже в воздухе!")
        elif key == ord('l'):
            if is_flying:
                print("Посадка!")
                me.land()
                is_flying = False
                me.send_rc_control(0, 0, 0, 0)
            else:
                print("Дрон уже на земле!")

except KeyboardInterrupt:
    print("\n Программа прервана")

finally:
    if is_flying:
        print("Посадка...")
        me.land()
        time.sleep(2)

    me.streamoff()
    me.end()
    cv2.destroyAllWindows()
    print("Программа завершена")