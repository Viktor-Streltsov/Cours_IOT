import cv2
from djitellopy import Tello
from ultralytics import YOLO
import time

# ПОДКЛЮЧЕНИЕ К ДРОНУ
print("Подключение к Tello...")
tello = Tello()

try:
    tello.connect(wait_for_state=False)
    print("Подключено к Tello!")
except Exception as e:
    print(f"Ошибка подключения: {e}")
    exit()

# Проверка батареи
battery = tello.get_battery()
print(f"Заряд батареи: {battery}%")

if battery < 20:
    print("⚠️ Слишком низкий заряд батареи! Подзарядите дрон.")
    tello.end()
    exit()

# ВИДЕОПОТОК
print("Включение видеопотока...")
tello.streamon()
frame_read = tello.get_frame_read()

# ЗАГРУЗКА МОДЕЛИ
print("Загрузка модели YOLOv8...")
model = YOLO('yolov8n.pt')
print("Модель загружена!")

# ОПТИМИЗАЦИЯ
# Счётчик кадров для пропуска (экономия ресурсов)
frame_counter = 0
SKIP_FRAMES = 2  # Обрабатываем каждый 2-й кадр

# Время для FPS
fps_time = time.time()
fps = 0

print("\n🎯 Нажмите 'q' для выхода")
print("📸 Нажмите 's' для сохранения кадра\n")

try:
    while True:
        # ПОЛУЧЕНИЕ КАДРА
        frame = frame_read.frame

        if frame is None:
            print("⚠️ Кадр не получен! Переподключение...")
            time.sleep(0.5)
            continue

        # Конвертация RGB -> BGR (для OpenCV)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Уменьшаем размер для скорости
        frame = cv2.resize(frame, (480, 360))

        # YOLO ИНФЕРЕНС
        frame_counter += 1

        # Обрабатываем не каждый кадр (экономия CPU)
        if frame_counter % SKIP_FRAMES == 0:
            # Детекция объектов (только люди, если нужно)
            # Для всех объектов: results = model(frame, conf=0.5)
            # Только люди (класс 0): results = model(frame, classes=[0], conf=0.5)
            results = model(frame, conf=0.5, imgsz=320)  # imgsz=320 для скорости

            # Визуализация
            for r in results:
                frame = r.plot()

                # Вывод информации в консоль
                if r.boxes is not None:
                    for box in r.boxes:
                        cls_id = int(box.cls)
                        cls_name = model.names[cls_id]
                        confidence = float(box.conf)
                        print(f"🔍 {cls_name}: {confidence:.2f}")

        # FPS СЧЁТЧИК
        current_time = time.time()
        if current_time - fps_time > 1.0:  # Обновляем каждую секунду
            fps = frame_counter / (current_time - fps_time)
            fps_time = current_time
            frame_counter = 0

        # Отображаем FPS на кадре
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # ОТОБРАЖЕНИЕ
        cv2.imshow('Tello YOLOv8', frame)

        # УПРАВЛЕНИЕ КЛАВИШАМИ
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n🚪 Выход...")
            break
        elif key == ord('s'):
            # Сохранение кадра
            filename = f"tello_yolo_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Кадр сохранён: {filename}")
        elif key == ord('t'):
            # Взлёт (опционально)
            print("🛫 Взлёт!")
            tello.takeoff()
        elif key == ord('l'):
            # Посадка (опционально)
            print("🛬 Посадка!")
            tello.land()

except KeyboardInterrupt:
    print("\n⚠️ Программа прервана пользователем")

finally:
    # ОЧИСТКА
    print("\n🧹 Очистка ресурсов...")
    tello.streamoff()
    tello.end()
    cv2.destroyAllWindows()
    print("✅ Программа завершена")