from cvzone.FaceMeshModule import FaceMeshDetector
import cv2

# НАСТРОЙКА
print("Запуск Face Mesh Detection...")

# Подключение к веб-камере
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Создание детектора
# maxFaces: максимальное количество лиц для детекции
# minDetectionCon: минимальная уверенность (0.5 = 50%)
detector = FaceMeshDetector(maxFaces=1, minDetectionCon=0.5)

# ОСНОВНОЙ ЦИКЛ
while True:
    # Чтение кадра
    success, img = cap.read()
    if not success:
        print("Ошибка: не удалось получить кадр")
        break

    # Зеркальное отражение для удобства
    img = cv2.flip(img, 1)

    # Детекция лица и получение сетки
    img, faces = detector.findFaceMesh(img, draw=True)

    # ОБРАБОТКА ДАННЫХ
    if faces:
        # faces[0] - список из 468 точек
        face_points = faces[0]

        # Вывод информации о первой точке
        print(f"Количество точек: {len(face_points)}")
        print(f"Точка 0 (нос): {face_points[0]}")
        print(f"Точка 1: {face_points[1]}")
        print(f"Точка 2: {face_points[2]}")
        print("---")

        # ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ
        # 1. Находим центр лица
        cx = int(sum([p[0] for p in face_points]) / len(face_points))
        cy = int(sum([p[1] for p in face_points]) / len(face_points))
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        cv2.putText(img, "Center", (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 2. Выделяем ключевые точки
        # Индексы ключевых точек (468 точек):
        # Нос: 1, 2, 4, 5
        # Глаза: 33 (левый), 263 (правый)
        # Рот: 61, 291

        # Рисуем точки на носу
        nose_points = [1, 2, 4, 5]
        for idx in nose_points:
            if idx < len(face_points):
                x, y, z = face_points[idx]
                cv2.circle(img, (int(x), int(y)), 3, (0, 0, 255), cv2.FILLED)

        # Рисуем точки глаз
        left_eye = 33
        right_eye = 263
        if left_eye < len(face_points):
            x, y, z = face_points[left_eye]
            cv2.circle(img, (int(x), int(y)), 5, (255, 0, 0), cv2.FILLED)
            cv2.putText(img, "L", (int(x) + 10, int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        if right_eye < len(face_points):
            x, y, z = face_points[right_eye]
            cv2.circle(img, (int(x), int(y)), 5, (255, 0, 0), cv2.FILLED)
            cv2.putText(img, "R", (int(x) + 10, int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 3. Вычисляем расстояние между глазами
        if left_eye < len(face_points) and right_eye < len(face_points):
            lx, ly = face_points[left_eye][0], face_points[left_eye][1]
            rx, ry = face_points[right_eye][0], face_points[right_eye][1]
            distance = ((lx - rx) ** 2 + (ly - ry) ** 2) ** 0.5
            cv2.putText(img, f"Eye distance: {distance:.1f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # ОТОБРАЖЕНИЕ
    cv2.imshow("Face Mesh Detection", img)

    # УПРАВЛЕНИЕ
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Выход...")
        break
    elif key == ord('s'):
        # Сохранение кадра с сеткой
        filename = f"face_mesh_{len(faces) if faces else 0}.jpg"
        cv2.imwrite(filename, img)
        print(f"Кадр сохранён: {filename}")

# ОЧИСТКА
cap.release()
cv2.destroyAllWindows()
print("Программа завершена")