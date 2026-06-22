"""Съёмка фото с дрона Tello Take a Picture & Save from Drone"""

import cv2
import time
from djitellopy import Tello
from datetime import datetime
import os

def main():
    """Основная функция для захвата фото с дрона Tello"""

    # НАСТРОЙКА ПАРАМЕТРОВ
    # Размер сохраняемого изображения (оптимально для Tello)
    SAVE_WIDTH = 480  # Желаемая ширина (оригинал: 960x720)
    SAVE_HEIGHT = 360  # Желаемая высота (оригинал: 960x720)

    # Папка для сохранения фото
    SAVE_DIR = "drone_photos"

    # Создаём папку, если её нет
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
        print(f"✓ Создана папка: {SAVE_DIR}")

    # ПОДКЛЮЧЕНИЕ К ДРОНУ
    print("\nПОДКЛЮЧЕНИЕ К ДРОНУ TELLO")

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

    # Проверка, достаточно ли заряда для полёта
    if battery_level < 20:
        print(f"⚠ ВНИМАНИЕ: Низкий заряд батареи ({battery_level}%)!")
        print("  Рекомендуется зарядить дрон перед полётом")

    # НАСТРОЙКА ВИДЕОПОТОКА
    print("\n НАСТРОЙКА ВИДЕОПОТОКА")

    # Включаем видеопоток
    tello.streamon()
    print("✓ Видеопоток включён")

    # Получаем объект для чтения кадров
    frame_read = tello.get_frame_read()

    # Ожидаем инициализации камеры
    print("⏳ Ожидание инициализации камеры...")
    time.sleep(2)
    print("✓ Камера готова")

    # ВЗЛЁТ (опционально)
    # Можно взлететь для съёмки с воздуха
    # tello.takeoff()
    # print("✓ Дрон взлетел")
    # time.sleep(2)  # Стабилизация после взлёта

    # ЗАХВАТ ФОТОГРАФИИ
    print("\n ЗАХВАТ ФОТОГРАФИИ")

    # Получаем текущий кадр
    frame = frame_read.frame

    # Проверка, получен ли кадр
    if frame is None:
        print("❌ Ошибка: Не удалось получить кадр с камеры!")
        tello.streamoff()
        return

    # Исходные размеры
    original_height, original_width = frame.shape[:2]
    print(f"✓ Исходное изображение: {original_width}x{original_height}")

    # ОБРАБОТКА ИЗОБРАЖЕНИЯ

    # 6.1 Изменение размера
    resized = cv2.resize(frame, (SAVE_WIDTH, SAVE_HEIGHT))
    print(f"✓ Изменён размер: {SAVE_WIDTH}x{SAVE_HEIGHT}")

    # 6.2 Дополнительная обработка (опционально)

    # Поворот изображения (если камера перевёрнута)
    # resized = cv2.rotate(resized, cv2.ROTATE_180)

    # Улучшение качества (опционально)
    # resized = cv2.convertScaleAbs(resized, alpha=1.2, beta=10)

    # Добавление информации на фото (опционально)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(resized, f"Tello Drone", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(resized, f"Battery: {battery_level}%", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(resized, timestamp, (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # СОХРАНЕНИЕ ФОТОГРАФИИ

    # Генерация имени файла с датой и временем
    filename = f"tello_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)

    # Сохранение изображения
    success = cv2.imwrite(filepath, resized)

    if success:
        print(f"✓ Фото сохранено: {filepath}")

        # Информация о размере файла
        file_size = os.path.getsize(filepath) / 1024  # Размер в KB
        print(f"✓ Размер файла: {file_size:.2f} KB")
    else:
        print("❌ Ошибка: Не удалось сохранить фотографию!")

    # ОТОБРАЖЕНИЕ ФОТО (опционально)

    # Показываем изображение в окне
    cv2.imshow('Tello Photo', resized)
    print("\nНажмите любую клавишу для закрытия окна...")
    cv2.waitKey(0)  # Ждём нажатия клавиши
    cv2.destroyAllWindows()

    # ПОСАДКА И ЗАВЕРШЕНИЕ
    print("\n ЗАВЕРШЕНИЕ")

    # Посадка (если взлетали)
    # tello.land()
    # print("✓ Дрон приземлился")

    # Отключение видеопотока
    tello.streamoff()
    print("✓ Видеопоток выключен")

    # Отключение от дрона
    tello.end()
    print("✓ Соединение закрыто")

    print(f"\n✅ Готово! Фото сохранено в папке: {SAVE_DIR}")


# ЗАПУСК
if __name__ == "__main__":
    main()