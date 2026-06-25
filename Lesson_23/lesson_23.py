"""Полётным паттерном в отдельном потоке"""

from djitellopy import Tello
import cv2
import time
from threading import Thread, Event
from datetime import datetime
import os


class TelloFlightController:
    """Класс для управления дроном с параллельной записью видео"""

    def __init__(self):
        # ПАРАМЕТРЫ
        self.speed = 25
        self.command_interval = 3  # Интервал между командами (сек)
        self.move_distance = 30  # Расстояние для движения (см)

        # Флаги управления
        self.landing_flag = False
        self.recording_flag = True
        self.video_writer = None

        # Счётчики
        self.frame_count = 0
        self.move_count = 0

        # ПОДКЛЮЧЕНИЕ К ДРОНУ
        print("\n ПОДКЛЮЧЕНИЕ К ДРОНУ TELLO")

        self.tello = Tello()

        try:
            self.tello.connect()
            print("✓ Подключение успешно!")
        except Exception as e:
            print(f" Ошибка подключения: {e}")
            return

        # Проверка батареи
        self.battery_level = self.tello.get_battery()
        print(f"✓ Заряд батареи: {self.battery_level}%")

        if self.battery_level < 20:
            print(f" ВНИМАНИЕ: Низкий заряд батареи ({self.battery_level})%!")

        # НАСТРОЙКА ВИДЕОПОТОКА
        print("\n НАСТРОЙКА ВИДЕОПОТОКА")

        self.tello.streamon()
        print("✓ Видеопоток включён")

        time.sleep(2)  # Ожидание инициализации
        print("✓ Камера готова")

        self.frame_read = self.tello.get_frame_read()

        # ПОДГОТОВКА К ЗАПИСИ
        # Создание папки для видео
        self.video_dir = "tello_videos"
        os.makedirs(self.video_dir, exist_ok=True)

        # Имя файла с датой и временем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_filename = os.path.join(self.video_dir, f"flight_{timestamp}.avi")

        print(f"✓ Видео будет сохранено: {self.video_filename}")

        # ИНФОРМАЦИЯ ОБ УПРАВЛЕНИИ
        print("\n=== УПРАВЛЕНИЕ ===")
        print("  q - выход и посадка")
        print("  p - пауза/возобновление движения")
        print("  s - скриншот")
        print("  SPACE - принудительная посадка")
        print("  + / - - изменить скорость")
        print("\n▶ Программа готова к работе!")

    def flight_pattern(self):
        """Поток выполнения полётного паттерна (вверх/вниз каждые 3 секунды)"""

        print("\n [ПОТОК ПОЛЁТА] Запуск...")

        try:
            # Взлёт
            print(" [ПОТОК ПОЛЁТА] Взлёт...")
            self.tello.takeoff()
            print("✓ [ПОТОК ПОЛЁТА] Дрон взлетел!")

            # Небольшая задержка для стабилизации
            time.sleep(2)

            # Начальное движение вверх
            print("⬆ [ПОТОК ПОЛЁТА] Подъём на 20 см")
            self.tello.move_up(20)

            # Переменные для цикла
            up_flag = True
            last_command_time = time.time()

            print(f"\n [ПОТОК ПОЛЁТА] Начинаю движение (интервал: {self.command_interval} сек)")

            # Основной цикл полёта
            while not self.landing_flag:
                current_time = time.time()

                # Проверяем, прошло ли нужное время
                if current_time - last_command_time >= self.command_interval:
                    last_command_time = current_time
                    self.move_count += 1

                    if up_flag:
                        # Движение вверх
                        print(f"⬆ [ПОТОК ПОЛЁТА] Вверх на {self.move_distance} см (#{self.move_count})")
                        self.tello.move_up(self.move_distance)
                        up_flag = False
                    else:
                        # Движение вниз
                        print(f"⬇ [ПОТОК ПОЛЁТА] Вниз на {self.move_distance} см (#{self.move_count})")
                        self.tello.move_down(self.move_distance)
                        up_flag = True

                # Небольшая задержка для снижения нагрузки на процессор
                time.sleep(0.1)

            # Посадка
            print("\n [ПОТОК ПОЛЁТА] Посадка...")
            self.tello.land()
            print("✓ [ПОТОК ПОЛЁТА] Дрон приземлился!")

        except Exception as e:
            print(f" [ПОТОК ПОЛЁТА] Ошибка: {e}")
            try:
                self.tello.land()
                print(" [ПОТОК ПОЛЁТА] Выполнена аварийная посадка")
            except:
                pass

        print("✅ [ПОТОК ПОЛЁТА] Завершён")

    def video_display(self):
        """Отображение видео (главный поток)"""
        print("\n ОТОБРАЖЕНИЕ ВИДЕО ")
        print(" Нажмите 'q' для выхода")

        # Создание VideoWriter для записи
        try:
            height, width, _ = self.frame_read.frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(
                self.video_filename,
                fourcc,
                25,
                (width, height)
            )
            print(f" Запись видео начата")
        except Exception as e:
            print(f" Ошибка создания VideoWriter: {e}")

        # Переменная для паузы движения
        pause_movement = False
        start_time = time.time()

        while True:
            try:
                # Получение кадра
                frame = self.frame_read.frame

                if frame is None:
                    print(" Пустой кадр, пропускаем...")
                    continue

                # Запись видео (если активна)
                if self.recording_flag and self.video_writer is not None:
                    self.video_writer.write(frame)
                    self.frame_count += 1

                # Подготовка кадра для отображения
                display = cv2.resize(frame, (640, 480))

                # ДОБАВЛЕНИЕ ИНФОРМАЦИИ НА ЭКРАН
                # Статус записи
                rec_status = "REC" if self.recording_flag else "PAUSE"
                rec_color = (0, 255, 0) if self.recording_flag else (0, 0, 255)
                cv2.putText(display, f"REC: {rec_status}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, rec_color, 2)

                # Информация о движении
                move_status = "⏸ PAUSED" if pause_movement else "▶ FLYING"
                cv2.putText(display, f"Move: {move_status}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                # Батарея и кадры
                cv2.putText(display, f"Battery: {self.battery_level}%", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(display, f"Frames: {self.frame_count}", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(display, f"Move #: {self.move_count}", (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Время работы
                elapsed = int(time.time() - start_time)
                cv2.putText(display, f"Time: {elapsed // 60}:{elapsed % 60:02d}", (10, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Скорость
                cv2.putText(display, f"Speed: {self.speed}", (10, 210),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Подсказки
                cv2.putText(display, "q-exit  p-pause  s-shot  SPACE-land",
                            (10, display.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

                # Отображение
                cv2.imshow("Tello Flight Control", display)

                # ОБРАБОТКА КЛАВИШ
                key = cv2.waitKey(1) & 0xFF

                # Выход (q)
                if key == ord('q'):
                    print("\n Выход по запросу пользователя")
                    self.landing_flag = True
                    break

                # Пауза движения (p)
                elif key == ord('p'):
                    pause_movement = not pause_movement
                    if pause_movement:
                        print(" [ГЛАВНЫЙ ПОТОК] Движение приостановлено")
                    else:
                        print(" [ГЛАВНЫЙ ПОТОК] Движение возобновлено")

                # Скриншот (s)
                elif key == ord('s'):
                    timestamp = datetime.now().strftime("%H%M%S")
                    filename = f"screenshot_{timestamp}.jpg"
                    cv2.imwrite(filename, display)
                    print(f" Скриншот сохранён: {filename}")

                # Принудительная посадка (SPACE)
                elif key == ord(' '):
                    print("[ГЛАВНЫЙ ПОТОК] Принудительная посадка!")
                    self.landing_flag = True
                    break

                # Изменение скорости (+)
                elif key == ord('+') or key == ord('='):
                    if self.speed < 100:
                        self.speed += 10
                        self.tello.set_speed(self.speed)
                        print(f" Скорость увеличена до: {self.speed}")

                # Изменение скорости (-)
                elif key == ord('-') or key == ord('_'):
                    if self.speed > 10:
                        self.speed -= 10
                        self.tello.set_speed(self.speed)
                        print(f" Скорость уменьшена до: {self.speed}")

            except Exception as e:
                print(f" Ошибка в основном цикле: {e}")
                break

        # ЗАВЕРШЕНИЕ
        print("\n ЗАВЕРШЕНИЕ ")

        # Останавливаем запись
        self.recording_flag = False
        if self.video_writer is not None:
            self.video_writer.release()
            print(f"✓ Видео сохранено: {self.video_filename}")

        # Выключаем видеопоток
        self.tello.streamoff()
        print("✓ Видеопоток выключен")

        # Закрываем окна
        cv2.destroyAllWindows()
        print("✓ Окна закрыты")

        # Статистика
        print(f"\n СТАТИСТИКА")
        print(f"Всего кадров: {self.frame_count}")
        if self.frame_count > 0:
            duration = time.time() - start_time
            fps = self.frame_count / duration
            print(f"Средний FPS: {fps:.1f}")
        print(f"Всего движений: {self.move_count}")

        print("\n✅ Программа завершена")

    def run(self):
        """Запуск параллельных потоков"""
        # Запуск потока полёта
        flight_thread = Thread(target=self.flight_pattern, daemon=False)
        flight_thread.start()
        print("✓ Поток полёта запущен")

        # Небольшая задержка для инициализации полёта
        time.sleep(1)

        # Запуск отображения видео (главный поток)
        self.video_display()

        # Ожидание завершения потока полёта
        flight_thread.join(timeout=5)
        print("✓ Поток полёта завершён")


# ЗАПУСК
if __name__ == "__main__":
    controller = TelloFlightController()
    controller.run()