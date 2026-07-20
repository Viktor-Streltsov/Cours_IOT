import cv2
from djitellopy import Tello

# Подключение к дрону
print("Подключение к Tello...")
tello = Tello()
tello.connect()

# Проверка батареи
battery_level = tello.get_battery()
print(f"Батарея: {battery_level}%")

if battery_level < 20:
    print("Слишком низкий заряд батареи!")
    exit()

# Включение видеопотока
print("Включение видеопотока...")
tello.streamon()
frame_read = tello.get_frame_read()

# Загрузка классификатора лиц
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascade_path)

# Проверка загрузки классификатора
if faceCascade.empty():
    print("Ошибка: не удалось загрузить классификатор!")
    exit()

print("Нажмите 'q' для выхода")

# Основной цикл
while True:
    # Получение кадра
    img = frame_read.frame

    # Проверка, что кадр получен
    if img is None:
        print("Ошибка: кадр не получен!")
        break

    # Конвертация RGB -> BGR (для OpenCV)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (480, 360))  # Уменьшаем для производительности

    # Детекция лиц
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    # Обработка найденных лиц
    for (x, y, w, h) in faces:
        # Рисуем прямоугольник вокруг лица
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Вычисляем центр лица
        cx = x + w // 2
        cy = y + h // 2
        area = w * h

        # Рисуем точку в центре лица
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        # Выводим информацию
        print(f"Лицо: центр=({cx}, {cy}), площадь={area}")

        # ДОПОЛНИТЕЛЬНО: можно добавить команды для дрона
        # Например, центрировать дрон по лицу:
        # if cx < 200: tello.move_left(20)
        # elif cx > 280: tello.move_right(20)

    # Показываем кадр
    cv2.imshow('Детекция лиц на Tello', img)

    # Выход по клавише 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Выход...")
        break

# Очистка ресурсов
print("Остановка видеопотока...")
tello.streamoff()
cv2.destroyAllWindows()
print("Программа завершена")