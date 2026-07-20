import cv2
from djitellopy import Tello

# ПОДКЛЮЧЕНИЕ К ДРОНУ
print("=" * 50)
print("Lab 35: Face Bounding Box Area")
print("=" * 50)

tello = Tello()
tello.connect()

battery_level = tello.get_battery()
print(f"Батарея: {battery_level}%")

if battery_level < 20:
    print("Низкий заряд батареи!")
    tello.end()
    exit()

# ВИДЕОПОТОК
tello.streamon()
frame_read = tello.get_frame_read()

# ЗАГРУЗКА МОДЕЛИ
faceCascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

print("\n Нажмите 'q' для выхода\n")

# ОСНОВНОЙ ЦИКЛ
while True:
    # Получение кадра
    img = frame_read.frame
    if img is None:
        continue

    # Конвертация RGB → BGR и изменение размера
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (480, 360))

    # Преобразование в оттенки серого для детекции лиц
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.3, 5)

    # СТАТУС ДЕТЕКЦИИ
    status = "Face Found" if len(faces) > 0 else "Face Not Found"
    color = (0, 255, 0) if len(faces) > 0 else (0, 0, 255)
    cv2.putText(img, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # ОБРАБОТКА ЛИЦ
    for (x, y, w, h) in faces:
        # 1. Рисуем прямоугольник вокруг лица (красный)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # 2. Вычисляем центр лица
        cx = x + w // 2
        cy = y + h // 2

        # 3. ВЫЧИСЛЯЕМ ПЛОЩАДЬ BOUNDING BOX
        area = w * h

        # 4. Рисуем центр лица (зелёный круг)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        # 5. Отображаем площадь на экране (над лицом)
        cv2.putText(img, f"Area: {area} px", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 6. Отображаем размеры (ширина × высота)
        cv2.putText(img, f"W: {w} H: {h}", (x, y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # 7. Отображаем координаты центра
        cv2.putText(img, f"Center: ({cx}, {cy})", (x, y + h + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # 8. Выводим информацию в консоль
        print(f"👤 Лицо: x={x}, y={y}, w={w}, h={h}, area={area}px")

    # ИНФОРМАЦИЯ НА ЭКРАНЕ
    # Количество найденных лиц
    cv2.putText(img, f"Faces: {len(faces)}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Уровень батареи
    cv2.putText(img, f"Battery: {tello.get_battery()}%", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # ОТОБРАЖЕНИЕ
    cv2.imshow('Lab 35: Face Bounding Box Area', img)

    # Выход по клавише 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ОЧИСТКА
tello.streamoff()
cv2.destroyAllWindows()
print("\n Lab 35 завершена")