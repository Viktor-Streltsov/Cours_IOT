import cv2
from djitellopy import Tello
from cvzone.FaceMeshModule import FaceMeshDetector
import cvzone
import time

# ПОДКЛЮЧЕНИЕ К ДРОНУ
print("=" * 50)
print(" Tello Face Mesh Detection")
print("=" * 50)

print("Подключение к Tello...")
me = Tello()

try:
    me.connect(wait_for_state=False)
    print(" Подключено к Tello!")
except Exception as e:
    print(f" Ошибка подключения: {e}")
    exit()

# Проверка батареи
battery = me.get_battery()
print(f"🔋 Заряд батареи: {battery}%")

if battery < 20:
    print("⚠️ Слишком низкий заряд батареи!")
    me.end()
    exit()

# ВИДЕОПОТОК
print(" Включение видеопотока...")
me.streamoff()  # Перезапуск на всякий случай
me.streamon()
time.sleep(1)  # Даём время на запуск

frame_read = me.get_frame_read()

# ИНИЦИАЛИЗАЦИЯ ДЕТЕКТОРА
# maxFaces: ограничиваем для производительности
# minDetectionCon: минимальная уверенность (0.5 = 50%)
detector = FaceMeshDetector(maxFaces=1, minDetectionCon=0.5)

# Счётчик FPS
fpsReader = cvzone.FPS()

print("\n Нажмите 'q' для выхода")
print(" Нажмите 's' для сохранения кадра\n")

# ОСНОВНОЙ ЦИКЛ
try:
    while True:
        # ПОЛУЧЕНИЕ КАДРА
        img = frame_read.frame

        if img is None:
            print("️ Кадр не получен!")
            time.sleep(0.5)
            continue

        # Конвертация RGB -> BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # ДЕТЕКЦИЯ ЛИЦА
        # findFaceMesh возвращает изображение с сеткой и список точек
        img, faces = detector.findFaceMesh(img, draw=True)

        # ОБРАБОТКА ДАННЫХ
        if faces:
            # faces[0] - список из 468 точек
            face_points = faces[0]

            # Вывод первых 5 точек (для отладки)
            print(f"👤 Обнаружено лицо: {len(face_points)} точек")
            print(f"  Точка 0 (нос): {face_points[0][:2]}")
            print(f"  Точка 1: {face_points[1][:2]}")
            print(f"  Точка 2: {face_points[2][:2]}")

            # ===== ОТОБРАЖЕНИЕ ИНФОРМАЦИИ =====
            # Находим центр лица
            cx = int(sum([p[0] for p in face_points]) / len(face_points))
            cy = int(sum([p[1] for p in face_points]) / len(face_points))
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f"Center: ({cx}, {cy})", (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Вывод количества точек
            cv2.putText(img, f"Points: {len(face_points)}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        else:
            cv2.putText(img, "No face detected", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # FPS
        fps, img = fpsReader.update(img)

        # ОТОБРАЖЕНИЕ
        cv2.imshow("Tello Face Mesh", img)

        # УПРАВЛЕНИЕ
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):  # Правильная кавычка!
            print(" Выход...")
            break
        elif key == ord('s'):
            # Сохранение кадра
            filename = f"tello_facemesh_{int(time.time())}.jpg"
            cv2.imwrite(filename, img)
            print(f" Кадр сохранён: {filename}")

except KeyboardInterrupt:
    print("\n Программа прервана пользователем")

finally:
    # ОЧИСТКА
    print("\n Очистка ресурсов...")
    me.streamoff()
    me.end()
    cv2.destroyAllWindows()
    print("✅ Программа завершена")