import cv2
from djitellopy import Tello

# ПОДКЛЮЧЕНИЕ К ДРОНУ
print("=" * 50)
print("Lab 34: Face Center vs Frame Center")
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

    # ВИЗУАЛИЗАЦИЯ ЦЕНТРА КАДРА
    # Центр кадра (tcx, tcy)
    tcx = img.shape[1] // 2
    tcy = img.shape[0] // 2

    # Рисуем центр кадра (синий круг)
    cv2.circle(img, (tcx, tcy), 10, (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f"Frame Center ({tcx}, {tcy})", (tcx + 15, tcy + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # ОБРАБОТКА ЛИЦ
    if len(faces) > 0:
        # Берём первое лицо
        (x, y, w, h) = faces[0]

        # Вычисляем центр лица (cx, cy)
        cx = x + w // 2
        cy = y + h // 2

        # Рисуем прямоугольник вокруг лица (красный)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Рисуем центр лица (зелёный круг)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f"Face Center ({cx}, {cy})", (cx + 15, cy + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # Линия от центра лица к центру кадра (синяя)
        cv2.line(img, (cx, cy), (tcx, tcy), (255, 0, 0), 2)

        # Отображение статуса
        cv2.putText(img, "FACE FOUND", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        cv2.putText(img, "NO FACE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # ОТОБРАЖЕНИЕ ИНФОРМАЦИИ
    cv2.putText(img, f"Battery: {tello.get_battery()}%", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Показываем кадр
    cv2.imshow('Lab 34: Face Center vs Frame Center', img)

    # Выход по клавише 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ОЧИСТКА
tello.streamoff()
cv2.destroyAllWindows()
print("\n Lab 34 завершена")