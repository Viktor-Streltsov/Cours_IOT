import cv2

# Открывае видео
cap = cv2.VideoCapture('video/video.mp4')

# Проверка открытия
if not cap.isOpened():
    print('Ошибка: не удалось открыть видео')
    exit()

# Получаем общее количество кадров
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# FPS видео (оригинальное)
video_fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Видео FPS: {video_fps}")
print(f"Всего кадров: {total_frames}")

frame_id = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Видео завершено")
        break

    frame_id += 1

    # Текущй FPS (приблизительный - зависит от waitKey)
    fps_text = f"Frame: {frame_id}/{total_frames}"

    # Добавляем текст на видео
    cv2.putText(
        frame,
        fps_text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 225, 0),
        2
    )

    # Показываем кадр
    cv2.imshow('frame', frame)

    # Управление скоростью воспроизведения
    key = cv2.waitKey(30) & 0xFF

    # Выход по 'q'
    if key == ord("q"):
        print("Выход из программы")
        break

cap.release()
cv2.destroyAllWindows()
