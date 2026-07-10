import cv2
import time
from djitellopy import Tello

# ======================================================
# 1. ПОДКЛЮЧЕНИЕ К ДРОНУ
# ======================================================
print("Подключение к дрону Tello...")
tello = Tello()

try:
    tello.connect()
    print("✅ Подключение успешно установлено!")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    exit()

battery_level = tello.get_battery()
print(f"🔋 Уровень заряда батареи: {battery_level}%")

if battery_level < 20:
    print("⚠️ Низкий заряд батареи!")
    exit()

# ======================================================
# 2. ВКЛЮЧЕНИЕ ВИДЕОПОТОКА
# ======================================================
tello.streamon()
time.sleep(2)  # Даем время на инициализацию
frame_read = tello.get_frame_read()

test_frame = frame_read.frame
if test_frame is None:
    print("❌ Ошибка: Не удается получить видеопоток")
    tello.streamoff()
    exit()
print("✅ Видеопоток активирован")

# ======================================================
# 3. ЗАГРУЗКА КЛАССИФИКАТОРА
# ======================================================
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    print("❌ Ошибка загрузки классификатора")
    tello.streamoff()
    exit()

# ======================================================
# 4. ПАРАМЕТРЫ
# ======================================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5
MIN_FACE_SIZE = (60, 60)
CENTER_TOLERANCE = 80

# Флаг слежения
tracking_mode = False
print("\n🎮 Управление:")
print("  'q' - Выход")
print("  't' - Взлет")
print("  'l' - Посадка")
print("  'w' - Вперед")
print("  's' - Назад")
print("  'a' - Влево")
print("  'd' - Вправо")
print("  'space' - Включить/выключить слежение за лицом")
print("  'r' - Вверх")
print("  'f' - Вниз\n")


# ======================================================
# 5. ФУНКЦИЯ ЦЕНТРИРОВАНИЯ (С ИСПРАВЛЕНИЕМ ТИПОВ)
# ======================================================
def center_face(face_x, face_y, face_w, face_h, frame_w, frame_h):
    """
    Возвращает команды для центрирования лица в кадре.
    ВАЖНО: преобразуем numpy.int32 в обычный int
    """
    # ПРЕОБРАЗОВАНИЕ ТИПОВ - вот решение ошибки!
    x = int(face_x)
    y = int(face_y)
    w = int(face_w)
    h = int(face_h)

    # Центр лица
    face_center_x = x + w // 2
    face_center_y = y + h // 2

    # Центр кадра
    center_x = frame_w // 2
    center_y = frame_h // 2

    # Смещение от центра
    dx = face_center_x - center_x
    dy = face_center_y - center_y

    commands = []

    # Вращение влево/вправо
    if abs(dx) > CENTER_TOLERANCE:
        if dx > 0:
            commands.append(('cw', 20))
        else:
            commands.append(('ccw', 20))

    # Движение вверх/вниз
    if abs(dy) > CENTER_TOLERANCE:
        if dy > 0:
            commands.append(('down', 20))
        else:
            commands.append(('up', 20))

    # Приближение/отдаление
    if w < 100 and h < 100:
        commands.append(('forward', 20))
    elif w > 250 and h > 250:
        commands.append(('back', 20))

    return commands


# ======================================================
# 6. ОСНОВНОЙ ЦИКЛ
# ======================================================
frame_counter = 0

try:
    while True:
        # Получение кадра
        img = frame_read.frame
        if img is None:
            print("⚠️ Потеря кадра...")
            continue

        # Конвертация RGB -> BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))

        # Оттенки серого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Детекция лиц
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=SCALE_FACTOR,
            minNeighbors=MIN_NEIGHBORS,
            minSize=MIN_FACE_SIZE
        )

        face_detected = len(faces) > 0

        # Отрисовка рамок для всех найденных лиц
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Face", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.circle(img, (x + w // 2, y + h // 2), 5, (0, 255, 255), -1)

        # ====================================================
        # СЛЕЖЕНИЕ ЗА ЛИЦОМ (исправленная логика)
        # ====================================================
        if tracking_mode and face_detected:
            # Берем первое найденное лицо
            (x, y, w, h) = faces[0]

            # Получаем команды для центрирования
            commands = center_face(x, y, w, h, FRAME_WIDTH, FRAME_HEIGHT)

            # Выполняем команды
            for cmd, value in commands:
                try:
                    if cmd == 'cw':
                        tello.rotate_clockwise(value)
                        print(f"↻ Поворот вправо на {value}")
                    elif cmd == 'ccw':
                        tello.rotate_counter_clockwise(value)
                        print(f"↺ Поворот влево на {value}")
                    elif cmd == 'up':
                        tello.move_up(value)
                        print(f"↑ Вверх на {value}")
                    elif cmd == 'down':
                        tello.move_down(value)
                        print(f"↓ Вниз на {value}")
                    elif cmd == 'forward':
                        tello.move_forward(value)
                        print(f"↗ Вперед на {value}")
                    elif cmd == 'back':
                        tello.move_back(value)
                        print(f"↘ Назад на {value}")
                except Exception as e:
                    print(f"⚠️ Ошибка выполнения команды: {e}")

            # Отображаем статус слежения
            cv2.putText(img, "TRACKING ACTIVE", (FRAME_WIDTH // 2 - 100, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        elif tracking_mode and not face_detected:
            cv2.putText(img, "NO FACE - TRACKING PAUSED", (FRAME_WIDTH // 2 - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Отображение информации
        cv2.putText(img, f"Battery: {tello.get_battery()}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(img, f"Faces: {len(faces)}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(img, f"Tracking: {'ON' if tracking_mode else 'OFF'}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 255) if tracking_mode else (0, 0, 255), 2)

        # Центр кадра
        cv2.drawMarker(img, (FRAME_WIDTH // 2, FRAME_HEIGHT // 2),
                       (255, 255, 255), cv2.MARKER_CROSS, 20, 2)

        cv2.imshow('Tello Face Tracking', img)

        # ====================================================
        # 7. УПРАВЛЕНИЕ С КЛАВИАТУРЫ
        # ====================================================
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Завершение программы...")
            break

        elif key == ord('t'):
            print("🛫 Взлет...")
            tello.takeoff()
            time.sleep(1)

        elif key == ord('l'):
            print("🛬 Посадка...")
            tello.land()
            time.sleep(1)

        elif key == ord('w'):
            print("⬆️ Вперед")
            tello.move_forward(30)

        elif key == ord('s'):
            print("⬇️ Назад")
            tello.move_back(30)

        elif key == ord('a'):
            print("⬅️ Влево")
            tello.move_left(30)

        elif key == ord('d'):
            print("➡️ Вправо")
            tello.move_right(30)

        elif key == ord('r'):
            print("🔼 Вверх")
            tello.move_up(30)

        elif key == ord('f'):
            print("🔽 Вниз")
            tello.move_down(30)

        elif key == ord(' '):  # Пробел - переключение режима слежения
            tracking_mode = not tracking_mode
            if tracking_mode:
                print("🎯 Режим слежения ВКЛЮЧЕН")
                if not face_detected:
                    print("⚠️ Лицо не найдено, слежение ожидает обнаружения")
            else:
                print("⏹ Режим слежения ВЫКЛЮЧЕН")

        # Обновление состояния батареи каждые 50 кадров
        frame_counter += 1
        if frame_counter % 50 == 0:
            bat = tello.get_battery()
            if bat < 20:
                print(f"⚠️ Низкий заряд батареи: {bat}%")

except KeyboardInterrupt:
    print("\n⚠️ Программа прервана пользователем")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ======================================================
# 8. ЗАВЕРШЕНИЕ
# ======================================================
finally:
    print("Остановка видеопотока...")
    tello.streamoff()
    cv2.destroyAllWindows()
    print("✅ Программа завершена")