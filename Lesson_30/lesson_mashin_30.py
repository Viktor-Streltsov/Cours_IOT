import cv2
from djitellopy import Tello
from ultralytics import YOLO
import time

# ПОДКЛЮЧЕНИЕ К ДРОНУ
print("=" * 50)
print("🚁 Tello YOLO Object Detection + Keyboard Control")
print("=" * 50)

print("Подключение к Tello...")
tello = Tello()

try:
    tello.connect(wait_for_state=False)
    print("✅ Подключено к Tello!")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    exit()

# Проверка батареи
battery = tello.get_battery()
print(f"🔋 Заряд батареи: {battery}%")

if battery < 20:
    print("⚠️ Слишком низкий заряд батареи! Подзарядите дрон.")
    tello.end()
    exit()

# ВИДЕОПОТОК
print("📹 Включение видеопотока...")
tello.streamon()
frame_read = tello.get_frame_read()
time.sleep(2)  # Даём время на запуск потока

# ЗАГРУЗКА МОДЕЛИ
print("🤖 Загрузка модели YOLOv8...")
model = YOLO('yolov8n.pt')
print("✅ Модель загружена!")

# ПЕРЕМЕННЫЕ ДЛЯ УПРАВЛЕНИЯ
# Скорость движения (см)
MOVE_SPEED = 20
ROTATE_SPEED = 20

# Флаги для удержания клавиш
move_keys = {
    'forward': False,
    'backward': False,
    'left': False,
    'right': False,
    'up': False,
    'down': False,
    'rotate_left': False,
    'rotate_right': False
}

# ОПТИМИЗАЦИЯ
frame_counter = 0
SKIP_FRAMES = 2
fps_time = time.time()
fps = 0
is_flying = False

# ВЫВОД УПРАВЛЕНИЯ
print("\n" + "=" * 50)
print("🎮 УПРАВЛЕНИЕ:")
print("=" * 50)
print("  t - Взлёт          l - Посадка")
print("  w - Вперёд         s - Назад")
print("  a - Влево          d - Вправо")
print("  ↑ - Вверх          ↓ - Вниз")
print("  q - Поворот влево  e - Поворот вправо")
print("  x - Аварийная остановка")
print("  r - Кувырок")
print("  space - Остановка")
print("  q (или Esc) - Выход")
print("=" * 50 + "\n")


# ФУНКЦИИ УПРАВЛЕНИЯ
def handle_keyboard(key):
    """Обработка нажатий клавиш"""
    global is_flying

    # Взлёт
    if key == ord('t'):
        if not is_flying:
            print("🛫 Взлёт!")
            tello.takeoff()
            is_flying = True
        else:
            print("⚠️ Дрон уже в воздухе!")
        return True

    # Посадка
    elif key == ord('l'):
        if is_flying:
            print("🛬 Посадка!")
            tello.land()
            is_flying = False
        else:
            print("⚠️ Дрон уже на земле!")
        return True

    # Аварийная остановка
    elif key == ord('x'):
        print("🛑 АВАРИЙНАЯ ОСТАНОВКА!")
        tello.emergency()
        is_flying = False
        return True

    # Кувырок
    elif key == ord('r'):
        if is_flying:
            print("🤸 Кувырок!")
            tello.flip_forward()
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    # Управление движением
    elif key == ord('w'):
        if is_flying:
            tello.move_forward(MOVE_SPEED)
            print(f"⬆️ Вперёд на {MOVE_SPEED} см")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    elif key == ord('s'):
        if is_flying:
            tello.move_backward(MOVE_SPEED)
            print(f"⬇️ Назад на {MOVE_SPEED} см")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    elif key == ord('a'):
        if is_flying:
            tello.move_left(MOVE_SPEED)
            print(f"⬅️ Влево на {MOVE_SPEED} см")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    elif key == ord('d'):
        if is_flying:
            tello.move_right(MOVE_SPEED)
            print(f"➡️ Вправо на {MOVE_SPEED} см")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    # Стрелки для высоты
    elif key == 82:  # Стрелка вверх
        if is_flying:
            tello.move_up(MOVE_SPEED)
            print(f"⬆️ Вверх на {MOVE_SPEED} см")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    elif key == 84:  # Стрелка вниз
        if is_flying:
            tello.move_down(MOVE_SPEED)
            print(f"⬇️ Вниз на {MOVE_SPEED} см")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    # Повороты
    elif key == ord('q'):
        if is_flying:
            tello.rotate_counter_clockwise(ROTATE_SPEED)
            print(f"🔄 Поворот влево на {ROTATE_SPEED}°")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    elif key == ord('e'):
        if is_flying:
            tello.rotate_clockwise(ROTATE_SPEED)
            print(f"🔄 Поворот вправо на {ROTATE_SPEED}°")
        else:
            print("⚠️ Дрон не в воздухе!")
        return True

    # Остановка
    elif key == ord(' '):
        print("⏹️ Остановка")
        return True

    # Выход
    elif key == 27:  # ESC
        print("🚪 Выход...")
        return False

    return True


# ОСНОВНОЙ ЦИКЛ
try:
    while True:
        # ПОЛУЧЕНИЕ КАДРА
        frame = frame_read.frame

        if frame is None:
            print("⚠️ Кадр не получен!")
            time.sleep(0.5)
            continue

        # Конвертация RGB -> BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (480, 360))

        # YOLO ДЕТЕКЦИЯ
        frame_counter += 1

        if frame_counter % SKIP_FRAMES == 0:
            results = model(frame, conf=0.5, imgsz=320)

            for r in results:
                frame = r.plot()

                # Вывод информации о найденных объектах
                if r.boxes is not None:
                    for box in r.boxes:
                        cls_id = int(box.cls)
                        cls_name = model.names[cls_id]
                        confidence = float(box.conf)
                        print(f"🔍 {cls_name}: {confidence:.2f}")

        # FPS
        current_time = time.time()
        if current_time - fps_time > 1.0:
            fps = frame_counter / (current_time - fps_time)
            fps_time = current_time
            frame_counter = 0

        # Отображение информации на кадре
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Battery: {tello.get_battery()}%", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Flying: {'YES' if is_flying else 'NO'}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Управление (отображаем на экране)
        cv2.putText(frame, "t:Takeoff l:Land w/s/a/d:Move", (10, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow('Tello YOLO + Keyboard Control', frame)

        # ОБРАБОТКА КЛАВИШ
        key = cv2.waitKey(1) & 0xFF

        # Обработка всех клавиш
        should_continue = handle_keyboard(key)
        if not should_continue:
            break

        # Выход по 'q'
        if key == ord('q'):
            break

except KeyboardInterrupt:
    print("\n⚠️ Программа прервана пользователем")

finally:
    # ОЧИСТКА
    print("\n🧹 Очистка ресурсов...")

    # Если дрон в воздухе - сажаем
    if is_flying:
        print("🛬 Посадка дрона...")
        try:
            tello.land()
            time.sleep(2)
        except:
            pass

    tello.streamoff()
    tello.end()
    cv2.destroyAllWindows()
    print("✅ Программа завершена")