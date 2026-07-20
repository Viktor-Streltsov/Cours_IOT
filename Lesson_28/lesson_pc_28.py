import cv2

# Загрузка классификатора лиц
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascade_path)

# Проверка загрузки классификатора
if faceCascade.empty():
    print("Ошибка: не удалось загрузить классификатор!")
    exit()

# Подключение к веб-камере (0 = встроенная камера, 1 = внешняя)
cap = cv2.VideoCapture(0)

# Проверка подключения камеры
if not cap.isOpened():
    print("Ошибка: не удалось открыть веб-камеру!")
    exit()

print("Нажмите 'q' для выхода")
print("Нажмите 's' для сохранения текущего кадра")

while True:
    # Чтение кадра с веб-камеры
    ret, frame = cap.read()

    if not ret:
        print("Ошибка: не удалось получить кадр с камеры!")
        break

    # Зеркальное отображение (для удобства, как в зеркале)
    frame = cv2.flip(frame, 1)

    # Уменьшаем размер для производительности (опционально)
    # frame = cv2.resize(frame, (640, 480))

    # Детекция лиц
    imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.1, 5)

    # Обработка найденных лиц
    for (x, y, w, h) in faces:
        # Рисуем прямоугольник вокруг лица
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Вычисляем центр лица
        cx = x + w // 2
        cy = y + h // 2
        area = w * h

        # Рисуем точку в центре лица
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

        # Добавляем подпись с координатами
        cv2.putText(frame, f"Face: ({cx}, {cy})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Отображаем количество найденных лиц
    cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Показываем результат
    cv2.imshow('Face Detection - Webcam', frame)

    # Обработка клавиш
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("Выход...")
        break
    elif key == ord('s'):
        # Сохранение текущего кадра
        filename = f"face_detection_{len(faces)}faces.jpg"
        cv2.imwrite(filename, frame)
        print(f"Кадр сохранён как {filename}")

# Очистка ресурсов
cap.release()
cv2.destroyAllWindows()
print("Программа завершена")