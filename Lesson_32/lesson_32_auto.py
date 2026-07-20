from cvzone.FaceMeshModule import FaceMeshDetector
import cv2

# НАСТРОЙКА
cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

# Индексы ключевых точек
LEFT_EYE = 33
RIGHT_EYE = 263
NOSE_TIP = 1
MOUTH_LEFT = 61
MOUTH_RIGHT = 291
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 23

# Переменные для отслеживания состояния
eye_closed = False
mouth_open = False

print("🎮 Управление:")
print("  Моргните = Движение вперёд")
print("  Откройте рот = Движение назад")
print("  Наклон головы = Поворот")
print("  Поворот головы = Вращение")
print("  q = Выход")

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img, faces = detector.findFaceMesh(img, draw=True)

    if faces:
        face = faces[0]

        # 1. Получение координат
        # Левый глаз
        lx, ly, lz = face[LEFT_EYE]
        rx, ry, rz = face[RIGHT_EYE]

        # Верх и низ левого глаза
        top_x, top_y, _ = face[LEFT_EYE_TOP]
        bot_x, bot_y, _ = face[LEFT_EYE_BOTTOM]

        # Рот
        mx1, my1, _ = face[MOUTH_LEFT]
        mx2, my2, _ = face[MOUTH_RIGHT]

        # Нос
        nx, ny, _ = face[NOSE_TIP]

        # 2. Анализ
        # Расстояние между глазами (для поворота головы)
        eye_distance = ((lx - rx) ** 2 + (ly - ry) ** 2) ** 0.5

        # Расстояние между веками (для моргания)
        eye_open = ((top_x - bot_x) ** 2 + (top_y - bot_y) ** 2) ** 0.5

        # Расстояние между углами рта (для открытия рта)
        mouth_distance = ((mx1 - mx2) ** 2 + (my1 - my2) ** 2) ** 0.5

        # 3. Отображение информации
        # Статус глаз
        if eye_open < 5:  # Если расстояние меньше порога
            cv2.putText(img, "😉 BLINK!", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            if not eye_closed:
                print("😉 Моргание!")
                eye_closed = True
        else:
            eye_closed = False

        # Статус рта
        if mouth_distance > 30:  # Если рот открыт
            cv2.putText(img, "👄 OPEN MOUTH", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            if not mouth_open:
                print("👄 Рот открыт!")
                mouth_open = True
        else:
            mouth_open = False

        # Положение носа (для движения влево/вправо)
        frame_center = img.shape[1] // 2
        if nx < frame_center - 50:
            cv2.putText(img, "⬅️ LOOK LEFT", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        elif nx > frame_center + 50:
            cv2.putText(img, "➡️ LOOK RIGHT", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # 4. Визуализация ключевых точек
        # Глаза
        cv2.circle(img, (int(lx), int(ly)), 5, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (int(rx), int(ry)), 5, (0, 255, 0), cv2.FILLED)

        # Рот
        cv2.circle(img, (int(mx1), int(my1)), 3, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (int(mx2), int(my2)), 3, (0, 0, 255), cv2.FILLED)

        # Нос
        cv2.circle(img, (int(nx), int(ny)), 5, (255, 0, 0), cv2.FILLED)

        # Отображение параметров
        cv2.putText(img, f"Eye open: {eye_open:.1f}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"Mouth: {mouth_distance:.1f}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Face Mesh Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()