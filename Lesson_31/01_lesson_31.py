"""
01. Базовое рисование в cvzone
--------------------------------
Две функции:
  - cvzone.cornerRect   — рамка со скруглёнными "уголками" (как в UI-дизайне)
  - cvzone.putTextRect  — текст с цветной подложкой

Запуск: python 01_lesson_31.py
Выход из окна: клавиша 'q'
"""

import cv2
import cvzone

# Индекс камеры: 0 — обычно встроенная веб-камера.
# Если подключена внешняя камера, попробуйте 1 или 2.
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        print("Не удалось получить кадр с камеры")
        break

    # --- Рамка со скруглёнными уголками ---
    img = cvzone.cornerRect(
        img,
        (200, 200, 300, 200),   # x, y, ширина, высота
        l=30,                    # длина уголка
        t=5,                     # толщина уголка
        rt=1,                    # толщина основной рамки
        colorR=(255, 0, 255),
        colorC=(0, 255, 0)
    )

    # --- Текст с подложкой ---
    img, bbox = cvzone.putTextRect(
        img, "CVZone", (50, 50),
        scale=3, thickness=3,
        colorT=(255, 255, 255), colorR=(255, 0, 255),
        font=cv2.FONT_HERSHEY_PLAIN,
        offset=10,
        border=5, colorB=(0, 255, 0)
    )

    cv2.imshow("01 - Basic Drawing", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
