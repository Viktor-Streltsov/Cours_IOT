import cv2
from djitellopy import Tello
import time

# ПОДКЛЮЧЕНИЕ К ДРОНУ

tello = Tello()
tello.connect()
print(f"Батарея: {tello.get_battery()}%")

if tello.get_battery() < 20:
    print("Низкий заряд батареи!")
    tello.end()
    exit()

# ВИДЕОПОТОК
tello.streamon()
time.sleep(1)
frame_read = tello.get_frame_read()

# ЗАГРУЗКА МОДЕЛИ
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# КОНФИГУРАЦИЯ
# Пороги площади лица (для разрешения 480x360)
# Чем меньше площадь, тем дальше лицо
TARGET_AREA_MIN = 8000  # Минимальная целевая площадь
TARGET_AREA_MAX = 20000  # Максимальная целевая площадь
MOVE_STEP = 20  # Шаг движения (см)

# Состояния
is_flying = False


# ФУНКЦИЯ УПРАВЛЕНИЯ
def adjust_tello_position(area):
    """
    Управление движением дрона вперёд/назад на основе площади лица.

    Параметры:
        area (int): Площадь bounding box лица (w * h)

    Логика:
        - Если лицо слишком маленькое (далеко) → двигаемся ВПЕРЁД
        - Если лицо слишком большое (близко) → двигаемся НАЗАД
        - Если лицо в целевой зоне → останавливаемся
    """
    global is_flying

    # Если дрон не в воздухе - не двигаемся
    if not is_flying:
        return

    # Если лицо не обнаружено (area = 0) - не двигаемся
    if area == 0:
        return

    # Проверяем, находится ли лицо в целевой зоне
    if TARGET_AREA_MIN <= area <= TARGET_AREA_MAX:
        # В целевой зоне - останавливаемся
        print(f"В зоне: area={area}")
        tello.send_rc_control(0, 0, 0, 0)  # Остановка
        return

    # Движение на основе площади
    if area < TARGET_AREA_MIN:
        # Лицо слишком маленькое → дрон далеко → двигаемся ВПЕРЁД
        print(f"ДАЛЕКО: area={area} < {TARGET_AREA_MIN} -> Вперёд!")
        tello.move_forward(MOVE_STEP)
    elif area > TARGET_AREA_MAX:
        # Лицо слишком большое → дрон близко → двигаемся НАЗАД
        print(f"БЛИЗКО: area={area} > {TARGET_AREA_MAX} -> Назад!")
        tello.move_back(MOVE_STEP)


#  ОСНОВНОЙ ЦИКЛ
print("\n УПРАВЛЕНИЕ:")
print("  [t] Взлёт  [l] Посадка  [q] Выход")
print("  [f] Вперёд (ручной)  [b] Назад (ручной)")
print("  Дрон автоматически регулирует расстояние по лицу!\n")

try:
    while True:
        # 1. ПОЛУЧЕНИЕ КАДРА
        frame = frame_read.frame
        if frame is None:
            print("⚠️ Кадр не получен!")
            time.sleep(0.5)
            continue

        # Конвертация RGB -> BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (480, 360))

        # 2. РАЗМЕРЫ КАДРА
        height, width = frame.shape[:2]
        center_x = width // 2
        center_y = height // 2

        # 3. ДЕТЕКЦИЯ ЛИЦ
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(60, 60)
        )

        # 4. ВИЗУАЛИЗАЦИЯ
        # Центр кадра (зелёный круг)
        cv2.circle(frame, (center_x, center_y), 8, (0, 255, 0), 3)
        cv2.putText(frame, "FRAME CENTER", (center_x + 15, center_y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # Рисуем зоны для визуализации
        # Целевая зона (зелёная рамка)
        cv2.rectangle(frame,
                      (center_x - 100, center_y - 100),
                      (center_x + 100, center_y + 100),
                      (0, 255, 0), 1)
        cv2.putText(frame, "TARGET ZONE", (center_x - 60, center_y - 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # 5. ОБРАБОТКА ЛИЦ
        z_area = 0  # Площадь лица (w * h)

        if len(faces) == 0:
            cv2.putText(frame, "[NO FACE]", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # Останавливаем движение, если лицо потеряно
            if is_flying:
                tello.send_rc_control(0, 0, 0, 0)
        else:
            # Берём первое лицо (самое большое)
            (x, y, w, h) = faces[0]
            z_area = w * h

            # Центр лица
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            # Рисуем прямоугольник вокруг лица (красный)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Рисуем центр лица (красный круг)
            cv2.circle(frame, (face_center_x, face_center_y), 8, (0, 0, 255), 3)

            # Линия от центра лица к центру кадра
            cv2.line(frame, (face_center_x, face_center_y),
                     (center_x, center_y), (255, 0, 0), 1)

            # Отображение информации о лице
            cv2.putText(frame, f"Face Area: {z_area}px", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Size: {w}x{h}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"Center: ({face_center_x}, {face_center_y})", (10, 85),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Отображение статуса расстояния
            if z_area < TARGET_AREA_MIN:
                cv2.putText(frame, "TOO FAR -> FORWARD", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            elif z_area > TARGET_AREA_MAX:
                cv2.putText(frame, "TOO CLOSE -> BACKWARD", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "PERFECT DISTANCE", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 6. УПРАВЛЕНИЕ ДРОНОМ
        adjust_tello_position(z_area)

        # 7. ИНФОРМАЦИЯ НА ЭКРАНЕ
        cv2.putText(frame, f"Battery: {tello.get_battery()}%", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Flying: {is_flying}", (10, 175),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Индикатор зон
        cv2.putText(frame, f"Target: {TARGET_AREA_MIN}-{TARGET_AREA_MAX}", (10, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # 8. ОТОБРАЖЕНИЕ
        cv2.imshow('Lab 36: Forward/Backward Control', frame)

        # 9. УПРАВЛЕНИЕ КЛАВИШАМИ
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Выход...")
            break
        elif key == ord('t'):
            if not is_flying:
                print("Взлёт!")
                tello.takeoff()
                tello.move_up(30)  # Поднимаемся на 30 см для безопасности
                is_flying = True
            else:
                print("Дрон уже в воздухе!")
        elif key == ord('l'):
            if is_flying:
                print("Посадка!")
                tello.land()
                is_flying = False
                tello.send_rc_control(0, 0, 0, 0)
            else:
                print("Дрон уже на земле!")
        elif key == ord('f'):
            # Ручное движение вперёд
            if is_flying:
                tello.move_forward(20)
                print("Вперёд (ручной)")
        elif key == ord('b'):
            # Ручное движение назад
            if is_flying:
                tello.move_back(20)
                print("Назад (ручной)")

except KeyboardInterrupt:
    print("\n Программа прервана пользователем")

finally:
    # 10. ОЧИСТКА
    print("\n Очистка ресурсов...")

    if is_flying:
        print("Посадка...")
        tello.land()
        time.sleep(2)

    tello.streamoff()
    tello.end()
    cv2.destroyAllWindows()
    print("Lab 36 завершена")