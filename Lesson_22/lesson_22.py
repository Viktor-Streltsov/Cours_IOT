import time
import cv2
from threading import Thread
from djitellopy import Tello
from datetime import datetime
import os

# ПОДКЛЮЧЕНИЕ
tello = Tello()
tello.connect()
print(f"Батарея: {tello.get_battery()}%")

tello.streamon()
frame_read = tello.get_frame_read()
time.sleep(2)

keep_recording = True
recording = True  # Флаг паузы записи
frame_count = 0


def video_recorder():
    """Запись видео в отдельном потоке"""
    global keep_recording, recording, frame_count

    # Получение размеров
    height, width, _ = frame_read.frame.shape

    # Создание папки для видео
    os.makedirs("tello_videos", exist_ok=True)
    filename = f"tello_videos/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"

    video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))
    print(f"Запись: {filename}")

    while keep_recording:
        try:
            frame = frame_read.frame

            if frame is None:
                continue

            # Запись видео (если не на паузе)
            if recording:
                video.write(frame)
                frame_count += 1

            # Отображение
            display = cv2.resize(frame, (640, 480))

            # Информация на экране
            status = "REC" if recording else "PAUSE"
            color = (0, 255, 0) if recording else (0, 0, 255)
            cv2.putText(display, f"{status}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(display, f"Frames: {frame_count}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, f"Battery: {tello.get_battery()}%", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, "q-quit p-pause s-screenshot", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            cv2.imshow('Tello Video', display)

            # Обработка клавиш
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                keep_recording = False
                break
            elif key == ord('p'):
                recording = not recording
                print(f"Запись: {'Включена' if recording else 'Приостановлена'}")
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%H%M%S")
                cv2.imwrite(f"screenshot_{timestamp}.jpg", display)
                print(f"Скриншот сохранён")

            time.sleep(1 / 30)

        except Exception as e:
            print(f"Ошибка: {e}")
            break

    video.release()
    cv2.destroyAllWindows()
    print(f"Запись завершена. Всего кадров: {frame_count}")


# ЗАПУСК ПОТОКА
recorder = Thread(target=video_recorder, daemon=True)
recorder.start()
print("Поток записи запущен")

# УПРАВЛЕНИЕ ДРОНОМ
time.sleep(1)

try:
    print("Взлёт...")
    tello.takeoff()
    time.sleep(2)

    print("Подъём...")
    tello.move_up(30)
    time.sleep(1)

    print("Поворот...")
    tello.rotate_counter_clockwise(360)
    time.sleep(2)

    print("Спуск...")
    tello.move_down(30)
    time.sleep(1)

    print("Посадка...")
    tello.land()

except KeyboardInterrupt:
    print("\n Прервано пользователем")
except Exception as e:
    print(f"Ошибка: {e}")
    tello.land()

# ЗАВЕРШЕНИЕ
keep_recording = False
recorder.join(timeout=5)

tello.streamoff()
cv2.destroyAllWindows()
print("✅ Программа завершена")