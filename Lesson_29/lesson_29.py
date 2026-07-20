import cv2
from ultralytics import YOLO

# Загрузка модели
print("Загрузка модели YOLOv8n...")
model = YOLO('yolov8n.pt')
print("Модель загружена!")

# Открытие веб-камеры
cap = cv2.VideoCapture(0)

# Настройка камеры для лучшей производительности
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Нажмите 'q' для выхода")
print("Нажмите 's' для сохранения кадра")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Ошибка: не удалось получить кадр")
        break

    # Зеркальное отражение для удобства
    frame = cv2.flip(frame, 1)

    # Запуск YOLO детекции
    results = model(frame, conf=0.5)  # Порог уверенности 50%

    # Обработка результатов
    for r in results:
        # Визуализация с рамками
        frame = r.plot()

        # Вывод информации в консоль
        if r.boxes is not None:
            for box in r.boxes:
                # Получаем имя класса и уверенность
                cls_id = int(box.cls)
                cls_name = model.names[cls_id]
                confidence = float(box.conf)

                # Выводим только лица (класс 0) если нужно
                # if cls_id == 0:  # Раскомментировать для фильтрации только людей
                print(f"Обнаружено: {cls_name} (уверенность: {confidence:.2f})")

    # Отображение кадра
    cv2.imshow('YOLO Object Detection', frame)

    # Обработка клавиш
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Выход...")
        break
    elif key == ord('s'):
        # Сохранение кадра
        filename = f"yolo_detection_{len(results[0].boxes)}objects.jpg"
        cv2.imwrite(filename, frame)
        print(f"Кадр сохранён как {filename}")

# Очистка ресурсов
cap.release()
cv2.destroyAllWindows()
print("Программа завершена")