"""
08. Lab 31 — Детекция лиц на видео с дрона Tello
----------------------------------------------------
Это исправленная версия лабораторной: детекция лиц (cvzone) применяется
к видеопотоку, который дрон Tello передаёт по Wi-Fi.

ПЕРЕД ЗАПУСКОМ:
  1. Установите библиотеки:
       pip install djitellopy
       pip install cvzone
       pip install mediapipe==0.10.9
  2. Включите дрон Tello и подключите компьютер к его Wi-Fi сети
     (имя сети начинается с "TELLO-...").
  3. Убедитесь, что дрон заряжен (см. значение батареи в консоли).

Выход из окна с видео: клавиша 'q'.
"""

import cv2
from djitellopy import Tello
from cvzone.FaceDetectionModule import FaceDetector

# --- Подключение к дрону ---
me = Tello()
me.connect()
print(f"Заряд батареи: {me.get_battery()}%")

# Поток видео нужно сначала выключить, затем включить —
# это устраняет проблему "зависшего" старого потока при повторном запуске
me.streamoff()
me.streamon()

detector = FaceDetector(minDetectionCon=0.5, modelSelection=0)

try:
    while True:
        frame = me.get_frame_read().frame
        if frame is None:
            continue

        # Кадр с Tello приходит в BGR-формате, размер обычно 960x720 —
        # можно уменьшить для более быстрой обработки:
        img = cv2.resize(frame, (640, 480))

        img, bboxs = detector.findFaces(img, draw=True)

        if bboxs:
            for bbox in bboxs:
                score = int(bbox['score'][0] * 100)
                x, y, w, h = bbox['bbox']
                cv2.putText(img, f'{score}%', (x, y - 10),
                            cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

        cv2.imshow("08 - Tello Face Detection", img)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
finally:
    # Важно освобождать поток и соединение, даже если произошла ошибка
    me.streamoff()
    cv2.destroyAllWindows()
