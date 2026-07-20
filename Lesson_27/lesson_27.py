import cv2
import time  # Для замера FPS (опционально)

# 1. ИНИЦИАЛИЗАЦИЯ ВЕБ-КАМЕРЫ С ПРОВЕРКОЙ

cap = cv2.VideoCapture(0)  # 0 - встроенная камера, 1 - внешняя

if not cap.isOpened():
    print("ОШИБКА: Не удалось открыть веб-камеру")
    print("Проверьте подключение камеры и повторите попытку")
    exit()

# 2. ЗАГРУЗКА КЛАССИФИКАТОРА

# Используем встроенный путь OpenCV к каскадам Хаара
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

# Проверка загрузки классификатора
if face_cascade.empty():
    print("ОШИБКА: Не удалось загрузить классификатор")
    print(f"Проверьте файл по пути: {cascade_path}")
    cap.release()
    exit()

print("Программа запущена успешно!")
print("Нажмите 'q' для выхода")

# 3. НАСТРОЙКА ПАРАМЕТРОВ ДЕТЕКЦИИ

# Рекомендуемые параметры для веб-камеры:
SCALE_FACTOR = 1.1  # 1.05-1.2 (меньше = точнее, но медленнее)
MIN_NEIGHBORS = 5  # 3-6 (больше = меньше ложных срабатываний)
MIN_FACE_SIZE = (60, 60)  # Минимальный размер лица для детекции
MAX_FACE_SIZE = (500, 500)  # Максимальный размер лица

# Размер кадра (уменьшаем для производительности)
FRAME_WIDTH = 640  # 640x480 - хороший баланс качество/скорость
FRAME_HEIGHT = 480

# 4. ОСНОВНОЙ ЦИКЛ ОБРАБОТКИ ВИДЕОПОТОКА

# Переменные для подсчета FPS (опционально)
fps_counter = 0
fps_start_time = time.time()
fps_display = "FPS: 0"

while True:
    # Захват кадра
    ret, frame = cap.read()
    if not ret:
        print("ОШИБКА: Не удалось захватить кадр")
        break

    # Изменение размера для ускорения обработки
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # Преобразование в оттенки серого (необходимо для каскадов Хаара)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 5. ДЕТЕКЦИЯ ЛИЦ

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=SCALE_FACTOR,
        minNeighbors=MIN_NEIGHBORS,
        minSize=MIN_FACE_SIZE,
        maxSize=MAX_FACE_SIZE
    )

    # 6. ОТРИСОВКА РЕЗУЛЬТАТОВ
    # Количество найденных лиц
    num_faces = len(faces)

    # Для каждого найденного лица рисуем рамку
    for (x, y, w, h) in faces:
        # Рисуем прямоугольник вокруг лица (зеленый - лучше виден)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Добавляем подпись "Face"
        cv2.putText(
            frame,
            "Face",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        # Дополнительно: можно добавить координаты лица
        # cv2.putText(frame, f"({x},{y})", (x, y + h + 20),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # 7. ОТОБРАЖЕНИЕ ИНФОРМАЦИИ НА КАДРЕ
    # Отображение количества лиц
    cv2.putText(
        frame,
        f"Faces: {num_faces}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # Отображение FPS (опционально)
    fps_counter += 1
    if time.time() - fps_start_time >= 1.0:
        fps_display = f"FPS: {fps_counter}"
        fps_counter = 0
        fps_start_time = time.time()

    cv2.putText(
        frame,
        fps_display,
        (FRAME_WIDTH - 120, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2
    )

    # Отображение подсказки по управлению
    cv2.putText(
        frame,
        "Press 'q' to quit",
        (10, FRAME_HEIGHT - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1
    )

    # 8. ВЫВОД РЕЗУЛЬТАТА НА ЭКРАН

    cv2.imshow('Face Detection - Webcam', frame)

    # Выход по нажатию клавиши 'q' или ESC
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # 27 = ESC
        print("Завершение программы по запросу пользователя")
        break

# 9. ОСВОБОЖДЕНИЕ РЕСУРСОВ

cap.release()
cv2.destroyAllWindows()
print("Программа завершена")