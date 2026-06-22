""" Чтение видео с веб-камеры и сохранение скриншета"""

import cv2

def main():
    """
    Основная функция для захвата и отображения видео с веб-камеры
    """

    # Инициализация захвата видео с камеры (0 - первая камера)
    # Можно указать путь к файлу вместо 0 для чтения из файла
    cap = cv2.VideoCapture(0)

    # Проверка успешности открытия камеры
    if not cap.isOpened():
        print("Ошибка: Не удалось открыть камеру!")
        return

    # Получение и вывод параметров видео (ширина и высота)
    # cap.get(3) - ширина кадра (CV_CAP_PROP_FRAME_WIDTH)
    # cap.get(4) - высота кадра (CV_CAP_PROP_FRAME_HEIGHT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f'Ширина: {width}, Высота: {height}')

    # Настройка FPS (опционально)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f'FPS: {fps}')

    print("Нажмите 'ESC' для выхода")
    print("Нажмите 'S' для сохранения текущего кадра")

    while True:
        # Захват кадра с камеры
        # ret - булево значение (True если кадр успешно захвачен)
        # frame - сам кадр (матрица пикселей)
        ret, frame = cap.read()

        # Проверка успешности захвата кадра
        if not ret:
            print("Ошибка: Не удалось получить кадр!")
            break

        # === ОПЦИОНАЛЬНЫЕ ОБРАБОТКИ ===
        # 1. Преобразование в оттенки серого (раскомментируйте при необходимости)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('video_gray', gray)

        # 2. Добавление текста на кадр (информация о времени)
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)

        # Отображение цветного видео в окне
        cv2.imshow('video', frame)

        # Обработка нажатий клавиш с задержкой 1 мс
        # waitKey(1) позволяет обновлять кадры с максимальной скоростью
        key = cv2.waitKey(1) & 0xFF

        # Выход по нажатию ESC (код 27)
        if key == 27:  # ESC
            print("Выход по нажатию ESC")
            break

        # Сохранение кадра по нажатию S (необязательная функция)
        elif key == ord('s') or key == ord('S'):
            # Сохранение текущего кадра в файл
            cv2.imwrite('screenshot.jpg', frame)
            print("Скриншот сохранён как 'screenshot.jpg'")

    # === ОСВОБОЖДЕНИЕ РЕСУРСОВ ===
    # 1. Освобождение камеры (обязательно)
    cap.release()

    # 2. Закрытие всех окон OpenCV (обязательно)
    cv2.destroyAllWindows()

    print("Программа завершена")

# Гарантированный запуск основной функции
if __name__ == "__main__":
    main()