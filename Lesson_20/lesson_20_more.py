"""Чтение видео с дрона Tello с помощью OpenCV Read Video from Drones using OpenCV"""

from djitellopy import Tello
import cv2
import time
from datetime import datetime


def main():
    """Основная функция для отображения видеопотока с дрона Tello"""

    # ПОДКЛЮЧЕНИЕ К ДРОНУ
    print("\n ПОДКЛЮЧЕНИЕ К ДРОНУ TELLO")

    # Создаём объект Tello
    tello = Tello()

    # Подключаемся к дрону
    try:
        tello.connect()
        print("✓ Подключение успешно!")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    # Проверка заряда батареи
    battery_level = tello.get_battery()
    print(f"✓ Заряд батареи: {battery_level}%")

    # Предупреждение о низком заряде
    if battery_level < 20:
        print(f"⚠ ВНИМАНИЕ: Низкий заряд батареи ({battery_level}%)!")

    # НАСТРОЙКА ВИДЕОПОТОКА
    print("\n НАСТРОЙКА ВИДЕОПОТОКА")

    # Включаем видеопоток
    tello.streamon()
    print("✓ Видеопоток включён")

    # Ожидаем инициализации камеры
    print("⏳ Ожидание инициализации камеры...")
    time.sleep(2)
    print("✓ Камера готова")

    # Получаем объект для чтения кадров
    frame_read = tello.get_frame_read()

    # ПАРАМЕТРЫ ОТОБРАЖЕНИЯ
    # Размер окна для отображения
    DISPLAY_WIDTH = 640  # Ширина окна
    DISPLAY_HEIGHT = 480  # Высота окна

    # Счётчик кадров
    frame_count = 0
    start_time = time.time()
    fps_display = 0

    print("\n=== УПРАВЛЕНИЕ ===")
    print("  'q' или 'Q' - выход")
    print("  's' или 'S' - сохранить скриншот")
    print("  'r' или 'R' - сбросить счётчик кадров")
    print("  'f' или 'F' - переключить зеркалирование")
    print("  'SPACE' - пауза/продолжить")
    print("  'ESC' - выход")
    print("\n▶ Видеопоток запущен...")

    # ПЕРЕМЕННЫЕ ДЛЯ УПРАВЛЕНИЯ
    paused = False  # Флаг паузы
    mirror_enabled = False  # Флаг зеркалирования
    show_info = True  # Показывать информацию на экране

    # ОСНОВНОЙ ЦИКЛ
    while True:
        # Если не на паузе - получаем кадр
        if not paused:
            # Получаем кадр с дрона
            tello_video_image = frame_read.frame

            # Проверка, получен ли кадр
            if tello_video_image is None:
                print("❌ Ошибка: Не удалось получить кадр с камеры!")
                break

            # Изменяем размер для отображения
            image = cv2.resize(tello_video_image, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

            # Опциональное зеркалирование
            if mirror_enabled:
                image = cv2.flip(image, 1)  # 1 - горизонтальное отражение

            # Счётчик кадров и FPS
            frame_count += 1
            if frame_count % 30 == 0:  # Обновляем FPS каждые 30 кадров
                elapsed_time = time.time() - start_time
                fps_display = int(frame_count / elapsed_time)

        # ДОБАВЛЕНИЕ ИНФОРМАЦИИ НА КАДР
        if show_info and not paused:
            # Текущее время
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Информация о статусе
            status = "▶ ЗАПИСЬ" if not paused else "⏸ ПАУЗА"
            color = (0, 255, 0) if not paused else (0, 0, 255)

            # Отображение информации на кадре
            cv2.putText(image, f"Tello Drone", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"Battery: {battery_level}%", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"FPS: {fps_display}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"Frames: {frame_count}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"Time: {timestamp}", (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"Status: {status}", (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Информация об управлении
            cv2.putText(image, "Q-exit  S-save  F-flip  SPACE-pause",
                        (10, DISPLAY_HEIGHT - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Если зеркалирование включено
            if mirror_enabled:
                cv2.putText(image, "MIRROR", (DISPLAY_WIDTH - 120, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # ОТОБРАЖЕНИЕ ВИДЕО
        cv2.imshow("Tello Video Stream", image)

        # ОБРАБОТКА НАЖАТИЙ КЛАВИШ
        # waitKey(1) - для плавного видео (задержка 1 мс)
        key = cv2.waitKey(1) & 0xFF

        # Выход по 'q' или 'Q'
        if key == ord('q') or key == ord('Q'):
            print("\n⏹ Выход по запросу пользователя")
            break

        # Выход по ESC
        elif key == 27:  # ESC
            print("\n⏹ Выход по ESC")
            break

        # Сохранение скриншота
        elif key == ord('s') or key == ord('S'):
            if not paused and 'image' in locals():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tello_screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, image)
                print(f"✓ Скриншот сохранён: {filename}")

        # Пауза/продолжить
        elif key == ord(' '):  # Пробел
            paused = not paused
            status = "приостановлен" if paused else "возобновлён"
            print(f"▶ Видеопоток {status}")
            if paused:
                cv2.putText(image, "PAUSED", (DISPLAY_WIDTH // 2 - 60, DISPLAY_HEIGHT // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                cv2.imshow("Tello Video Stream", image)

        # Переключить зеркалирование
        elif key == ord('f') or key == ord('F'):
            mirror_enabled = not mirror_enabled
            print(f"🔄 Зеркалирование: {'Включено' if mirror_enabled else 'Выключено'}")

        # Сбросить счётчик кадров
        elif key == ord('r') or key == ord('R'):
            frame_count = 0
            start_time = time.time()
            print("🔄 Счётчик кадров сброшен")

        # Переключить отображение информации
        elif key == ord('i') or key == ord('I'):
            show_info = not show_info
            print(f"ℹ Информация: {'Показана' if show_info else 'Скрыта'}")

    # ЗАВЕРШЕНИЕ
    print("\n ЗАВЕРШЕНИЕ")

    # Отключение видеопотока
    tello.streamoff()
    print("✓ Видеопоток выключен")

    # Закрытие всех окон
    cv2.destroyAllWindows()
    print("✓ Окна закрыты")

    # Отключение от дрона
    tello.end()
    print("✓ Соединение закрыто")

    # Статистика
    if frame_count > 0:
        duration = time.time() - start_time
        print(f"\n=== СТАТИСТИКА ===")
        print(f"Всего кадров: {frame_count}")
        print(f"Длительность: {duration:.2f} секунд")
        print(f"Средний FPS: {frame_count / duration:.1f}")

    print("\n✅ Программа завершена")


# ЗАПУСК
if __name__ == "__main__":
    main()