"""Лабораторная работа 18: Сохранение видео с веб-камеры"""

import cv2
import time

def main():
    """
    Основная функция для захвата и сохранения видео с веб-камеры
    """

    # 1. Инициализация захвата видео с камеры
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Ошибка: Не удалось открыть камеру!")
        return

    # 2. Определение параметров видео (реальное разрешение камеры)
    # ВАЖНО: Используем фактические размеры кадра, чтобы избежать ошибок несоответствия
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Ширина
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Высота
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0  # Получаем FPS камеры или ставим 25.0

    print(f"Разрешение видео: {frame_width}x{frame_height}")
    print(f"FPS: {fps}")

    # 3. Настройка кодека (четырёхсимвольный код - FourCC)
    # Доступные кодеки: DIVX, XVID, MJPG, X264, WMV1, WMV2, MP4V, FMP4, I420
    # fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # 'DIVX' - для AVI файлов

    # Альтернативные варианты кодеков:
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Также хорошо для AVI
    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Для AVI с высоким качеством
    # fourcc = cv2.VideoWriter_fourcc(*'X264')  # Для MP4 файлов (нужно изменить расширение)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Для MP4 (стандартный)

    # 4. Создание объекта VideoWriter для сохранения видео
    out = cv2.VideoWriter(
        'output.mp4',  # Имя выходного файла
        fourcc,  # Кодек
        fps,  # Количество кадров в секунду
        (frame_width, frame_height)  # Размер кадра (ширина, высота)
    )

    # Проверка успешности создания VideoWriter
    if not out.isOpened():
        print("Ошибка: Не удалось создать VideoWriter!")
        cap.release()
        return

    print("\nЗапись видео начата...")
    print("Нажмите 'q' для остановки записи и выхода")
    print("Нажмите 'p' для паузы/возобновления записи")

    # 5. Переменные для управления записью
    recording = True  # Флаг записи (True - запись, False - пауза)
    frame_count = 0  # Счётчик записанных кадров

    # 6. Основной цикл захвата и записи видео
    while cap.isOpened():
        # Захват кадра
        ret, frame = cap.read()

        if not ret:
            print("Ошибка: Не удалось получить кадр!")
            break

        # 7. Обработка кадра (зеркальное отражение)
        # flip(frame, 0) - отражение по вертикали (верх-низ)
        # flip(frame, 1) - отражение по горизонтали (лево-право)
        # flip(frame, -1) - отражение по обеим осям (поворот на 180°)
        flipped_frame = cv2.flip(frame, 0)  # Зеркальное отражение сверху-вниз

        # 8. Добавление информации на кадр (опционально)
        # Текущее время
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(flipped_frame, f"Recording: {recording}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(flipped_frame, f"Frames: {frame_count}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(flipped_frame, f"Time: {timestamp}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 9. Запись кадра в файл (если запись активна)
        if recording:
            out.write(flipped_frame)
            frame_count += 1

        # 10. Отображение видео в окне
        cv2.imshow('Video Recording', flipped_frame)

        # 11. Обработка нажатий клавиш с задержкой 1 мс
        # waitKey(1) - обеспечивает плавное воспроизведение
        key = cv2.waitKey(1) & 0xFF

        # Q - выход и остановка записи
        if key == ord('q'):
            print("\nОстановка записи по команде пользователя")
            break

        # P - пауза/возобновление записи
        elif key == ord('p'):
            recording = not recording
            status = "возобновлена" if recording else "приостановлена"
            print(f"Запись {status}")

        # S - сохранение скриншота (дополнительная функция)
        elif key == ord('s') or key == ord('S'):
            screenshot_name = f"screenshot_{int(time.time())}.jpg"
            cv2.imwrite(screenshot_name, flipped_frame)
            print(f"Скриншот сохранён как '{screenshot_name}'")

    # 12. Освобождение ресурсов (всегда выполняйте в конце)
    print(f"\nВсего записано кадров: {frame_count}")

    cap.release()  # Освобождаем камеру
    out.release()  # Освобождаем видеозапись (закрывает файл)
    cv2.destroyAllWindows()  # Закрываем все окна OpenCV

    print("Программа завершена")
    print(f"Видео сохранено в файл: output.avi")


if __name__ == "__main__":
    main()