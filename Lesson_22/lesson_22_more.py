"""Параллельная запись видео и управление дроном с помощью потоков"""

import time
import cv2
from threading import Thread
from djitellopy import Tello
from datetime import datetime
import os


class TelloVideoRecorder:
    """Класс для параллельной записи видео и управления дронов"""

    def __init__(self):
        # ПОДКЛЮЧЕНИЕ К ДРОНУ
        print("\n ПОДКЛЮЧЕНИЕ К ДРОНУ TELLO")

        self.tello = Tello()
        self.tello.connect()
        print("✓ Подключение успешно!")

        # Проверка батареи
        self.battery_level = self.tello.get_battery()
        print(f"✓ Заряд батареи: {self.battery_level}%")

        if self.battery_level < 20:
            print(f"⚠ ВНИМАНИЕ: Низкий заряд батареи ({self.battery_level})%!")

        # НАСТРОЙКА ВИДЕОПОТОКА
        print("\n НАСТРОЙКА ВИДЕОПОТОКА ")

        self.tello.streamon()
        print("✓ Видеопоток включён")

        time.sleep(2)  # Ожидание инициализации камеры
        print("✓ Камера готова")

        self.frame_read = self.tello.get_frame_read()

        # ПАРАМЕТРЫ ЗАПИСИ
        self.keep_recording = True
        self.fps = 30
        self.video_writer = None

        # Создание папки для видео
        self.video_dir = "tello_videos"
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)
            print(f"✓ Создана папка: {self.video_dir}")

        # Имя файла с датой и временем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_filename = os.path.join(self.video_dir, f"tello_video_{timestamp}.avi")

        print(f"✓ Видео будет сохранено: {self.video_filename}")

        # ПЕРЕМЕННЫЕ ДЛЯ СТАТИСТИКИ
        self.frame_count = 0
        self.start_time = time.time()
        self.is_recording = False

        print("\n▶ Система готова к работе!")
        print("  Запись видео будет начата автоматически")
        print("  Нажмите 'q' для остановки записи\n")

    def video_recorder(self):
        """Функция записи видео в отдельном потоке"""
        print("[RECORDER] Запуск записи видео...")

        # Получение размеров кадра
        frame = self.frame_read.frame
        if frame is None:
            print("[RECORDER] Ошибка: Не удалось получить кадр!")
            return

        height, width, _ = frame.shape
        print(f" [RECORDER] Разрешение видео: {width}x{height}")

        # Создание VideoWriter
        try:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(
                self.video_filename,
                fourcc,
                self.fps,
                (width, height)
            )

            if not self.video_writer.isOpened():
                print("[RECORDER] Ошибка создания VideoWriter!")
                return

            print("✓ [RECORDER] VideoWriter создан успешно")

        except Exception as e:
            print(f"[RECORDER] Ошибка: {e}")
            return

        self.is_recording = True

        # Основной цикл записи
        while self.keep_recording:
            try:
                # Получение кадра
                frame = self.frame_read.frame

                if frame is None:
                    print(" [RECORDER] Пустой кадр, пропускаем...")
                    continue

                # Запись видео
                self.video_writer.write(frame)
                self.frame_count += 1

                # Отображение видео
                display = cv2.resize(frame, (640, 480))

                # Добавление информации на экран
                cv2.putText(display, f"RECORDING", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display, f"Frames: {self.frame_count}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(display, f"Battery: {self.battery_level}%", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                cv2.imshow('Tello Video Recording', display)

                # Проверка нажатия 'q' для остановки
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n [RECORDER] Остановка по запросу пользователя")
                    self.keep_recording = False
                    break

                # Контроль FPS
                time.sleep(1 / self.fps)

            except Exception as e:
                print(f"[RECORDER] Ошибка в цикле записи: {e}")
                break

        # Освобождение ресурсов
        if self.video_writer is not None:
            self.video_writer.release()
            print(f"✓ [RECORDER] Видео сохранено: {self.video_filename}")

        self.is_recording = False
        print(f"📹 [RECORDER] Всего записано кадров: {self.frame_count}")
        cv2.destroyAllWindows()
        print("✓ [RECORDER] Поток завершён")

    def fly_drone(self):
        """Функция управления дроном (выполняется в основном потоке)"""
        print("\n УПРАВЛЕНИЕ ДРОНОМ")

        try:
            # Взлёт
            print(" Взлёт...")
            self.tello.takeoff()
            print("✓ Дрон взлетел!")
            time.sleep(2)

            # Движение вверх
            print("⬆ Подъём на 30 см...")
            self.tello.move_up(30)
            print("✓ Подъём выполнен")
            time.sleep(1)

            # Поворот на 360°
            print("Поворот на 360° против часовой...")
            self.tello.rotate_counter_clockwise(360)
            print("✓ Поворот завершён!")
            time.sleep(1)

            # Дополнительные манёвры (опционально)
            print("⬇ Вниз на 30 см...")
            self.tello.move_down(30)
            print("✓ Опускание выполнено")
            time.sleep(1)

            # Посадка
            print("Посадка...")
            self.tello.land()
            print("✓ Дрон приземлился!")

        except Exception as e:
            print(f"Ошибка при управлении дроном: {e}")
            try:
                self.tello.land()
                print("Выполнена аварийная посадка")
            except:
                print("Ошибка при аварийной посадке")

    def run(self):
        """Запуск параллельных потоков"""
        print("\n ЗАПУСК ПАРАЛЛЕЛЬНЫХ ПОТОКОВ ")

        # Создание и запуск потока записи видео
        recorder_thread = Thread(target=self.video_recorder, daemon=True)
        recorder_thread.start()
        print("✓ Поток записи видео запущен")

        # Даём время на инициализацию записи
        time.sleep(1)

        # Выполнение полёта в основном потоке
        try:
            self.fly_drone()
        except Exception as e:
            print(f"Ошибка во время полёта: {e}")

        # Остановка записи
        print("\n Остановка записи видео...")
        self.keep_recording = False

        # Ожидание завершения потока записи
        recorder_thread.join(timeout=5)
        print("✓ Поток записи остановлен")

        # ===== 5. ЗАВЕРШЕНИЕ =====
        print("\n=== ЗАВЕРШЕНИЕ ===")

        # Отключение видеопотока
        self.tello.streamoff()
        print("✓ Видеопоток выключен")

        # Закрытие всех окон
        cv2.destroyAllWindows()
        print("✓ Окна закрыты")

        # Отключение от дрона
        self.tello.end()
        print("✓ Соединение закрыто")

        # Статистика
        print(f"\n=== СТАТИСТИКА ===")
        print(f"Записано кадров: {self.frame_count}")
        if self.frame_count > 0:
            duration = time.time() - self.start_time
            actual_fps = self.frame_count / duration
            print(f"Длительность: {duration:.2f} секунд")
            print(f"Средний FPS: {actual_fps:.1f}")

        # Проверка файла
        if os.path.exists(self.video_filename):
            file_size = os.path.getsize(self.video_filename) / (1024 * 1024)
            print(f"Размер файла: {file_size:.2f} MB")
            print(f"Файл сохранён: {self.video_filename}")

        print("\n✅ Программа завершена")


# ЗАПУСК
if __name__ == "__main__":
    app = TelloVideoRecorder()
    app.run()