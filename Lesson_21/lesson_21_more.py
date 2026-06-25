""" Управление дроном Tello с клавиатуры через OpenCV"""

from djitellopy import Tello
import cv2
import time

def main():
    """Основная функция для управления дроном Tello с клавиатуры """

    # ПОДКЛЮЧЕНИЕ К ДРОНУ
    print("\n=== ПОДКЛЮЧЕНИЕ К ДРОНУ TELLO ===")

    tello = Tello()

    try:
        tello.connect()
        print("✓ Подключение успешно!")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    # Проверка батареи
    battery_level = tello.get_battery()
    print(f"✓ Заряд батареи: {battery_level}%")

    if battery_level < 20:
        print(f"⚠ ВНИМАНИЕ: Низкий заряд батареи ({battery_level}%)!")
        print("  Рекомендуется зарядить дрон перед полётом")

    # НАСТРОЙКА ВИДЕОПОТОКА
    print("\n НАСТРОЙКА ВИДЕОПОТОКА ")

    tello.streamon()
    print("✓ Видеопоток включён")

    time.sleep(2)  # Ожидание инициализации камеры
    print("✓ Камера готова")

    frame_read = tello.get_frame_read()

    # ПАРАМЕТРЫ ОТОБРАЖЕНИЯ
    DISPLAY_WIDTH = 720  # Ширина окна
    DISPLAY_HEIGHT = 480  # Высота окна

    # ОТОБРАЖЕНИЕ УПРАВЛЕНИЯ
    print("\nУПРАВЛЕНИЕ ДРОНОМ")
    print("┌─────────────────────────────────────────────────────┐")
    print("│  КЛАВИША  │  ДЕЙСТВИЕ                            │")
    print("├─────────────────────────────────────────────────────┤")
    print("│  t       │  Взлёт (Takeoff)                     │")
    print("│  l       │  Посадка (Land)                      │")
    print("│  w       │  Вперёд (Forward)                    │")
    print("│  s       │  Назад (Backward)                    │")
    print("│  a       │  Влево (Left)                        │")
    print("│  d       │  Вправо (Right)                      │")
    print("│  ↑ (Up)  │  Вверх (Up)                          │")
    print("│  ↓ (Down)│  Вниз (Down)                         │")
    print("│  ← (Left)│  Поворот налево (Rotate CCW)         │")
    print("│  → (Right)│  Поворот направо (Rotate CW)        │")
    print("│  c       │  Поворот на 360° (Circle)            │")
    print("│  f       │  Переключить зеркалирование          │")
    print("│  space   │  Пауза/возобновление видеопотока     │")
    print("│  q       │  Выход и посадка                     │")
    print("│  ESC     │  Аварийная остановка                 │")
    print("└─────────────────────────────────────────────────────┘")

    # ПЕРЕМЕННЫЕ ДЛЯ УПРАВЛЕНИЯ
    speed = 50  # Скорость движения (по умолчанию 50)
    distance = 50  # Расстояние для движения (по умолчанию 50 см)
    mirror_enabled = False  # Зеркалирование
    paused = False  # Пауза
    frame_count = 0  # Счётчик кадров
    last_action = "Ожидание"  # Последнее действие

    print("\n▶ Дрон готов к управлению!")
    print(f"Скорость: {speed} | Дистанция: {distance}см")

    # ОСНОВНОЙ ЦИКЛ
    while True:
        # Получение кадра (если не на паузе)
        if not paused:
            frame = frame_read.frame

            if frame is None:
                print("❌ Ошибка получения кадра!")
                continue

            # Изменение размера для отображения
            display = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

            # Зеркалирование (опционально)
            if mirror_enabled:
                display = cv2.flip(display, 1)

            # ДОБАВЛЕНИЕ ИНФОРМАЦИИ НА ЭКРАН
            # Статус
            status = "▶ ЗАПИСЬ" if not paused else "⏸ ПАУЗА"
            status_color = (0, 255, 0) if not paused else (0, 0, 255)

            # Информация о дроне
            cv2.putText(display, f"Tello Drone", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"Battery: {battery_level}%", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"Status: {status}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.putText(display, f"Action: {last_action}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            # Информация об управлении
            cv2.putText(display, f"Speed: {speed} | Dist: {distance}cm",
                        (10, DISPLAY_HEIGHT - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display, "t-takeoff l-land w/s/a/d-move arrows-rotate",
                        (10, DISPLAY_HEIGHT - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            # Если зеркалирование включено
            if mirror_enabled:
                cv2.putText(display, "MIRROR", (DISPLAY_WIDTH - 120, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Отображение видео
            cv2.imshow("Tello Drone Control", display)
            frame_count += 1

        # ОБРАБОТКА КЛАВИШ
        key = cv2.waitKey(5) & 0xFF  # Задержка 5 мс для плавности

        # ОСНОВНЫЕ КОМАНДЫ ДРОНА

        # Взлёт (t)
        if key == ord('t'):
            print("🛫 Взлёт...")
            try:
                tello.takeoff()
                last_action = "Взлёт"
                print("✓ Дрон взлетел!")
            except Exception as e:
                print(f"❌ Ошибка взлёта: {e}")
                last_action = "Ошибка взлёта"

        # Посадка (l)
        elif key == ord('l'):
            print("🛬 Посадка...")
            try:
                tello.land()
                last_action = "Посадка"
                print("✓ Дрон приземлился!")
            except Exception as e:
                print(f"❌ Ошибка посадки: {e}")
                last_action = "Ошибка посадки"

        # ДВИЖЕНИЕ ПО КОМАНДАМ WASD

        # Вперёд (w)
        elif key == ord('w'):
            print(f"⬆ Вперёд: {distance}см")
            tello.move_forward(distance)
            last_action = f"Вперёд {distance}см"

        # Назад (s)
        elif key == ord('s'):
            print(f"⬇ Назад: {distance}см")
            tello.move_back(distance)
            last_action = f"Назад {distance}см"

        # Влево (a)
        elif key == ord('a'):
            print(f"⬅ Влево: {distance}см")
            tello.move_left(distance)
            last_action = f"Влево {distance}см"

        # Вправо (d)
        elif key == ord('d'):
            print(f"➡ Вправо: {distance}см")
            tello.move_right(distance)
            last_action = f"Вправо {distance}см"

        # СТРЕЛКИ ДЛЯ ПОВОРОТОВ И ВЕРТИКАЛЬНОГО ДВИЖЕНИЯ

        # Вверх (стрелка вверх)
        elif key == ord(' ') or key == 0:  # Базовое условие
            pass  # Пропускаем, чтобы не конфликтовать

        # Стрелка вверх - движение вверх
        elif key == 82:  # Код стрелки вверх (в OpenCV)
            print(f"⬆ Вверх: {distance}см")
            tello.move_up(distance)
            last_action = f"Вверх {distance}см"

        # Стрелка вниз - движение вниз
        elif key == 84:  # Код стрелки вниз
            print(f"⬇ Вниз: {distance}см")
            tello.move_down(distance)
            last_action = f"Вниз {distance}см"

        # Стрелка влево - поворот налево
        elif key == 81:  # Код стрелки влево
            print(f"↺ Поворот налево: 30°")
            tello.rotate_counter_clockwise(30)
            last_action = "Поворот налево 30°"

        # Стрелка вправо - поворот направо
        elif key == 83:  # Код стрелки вправо
            print(f"↻ Поворот направо: 30°")
            tello.rotate_clockwise(30)
            last_action = "Поворот направо 30°"

        # ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ

        # Поворот на 360° (c)
        elif key == ord('c'):
            print("🔄 Поворот на 360°...")
            try:
                tello.rotate_clockwise(360)
                last_action = "Поворот 360°"
                print("✓ Поворот завершён!")
            except Exception as e:
                print(f"❌ Ошибка поворота: {e}")
                last_action = "Ошибка поворота"

        # РЕГУЛИРОВКА СКОРОСТИ И ДИСТАНЦИИ

        # Увеличение скорости (+)
        elif key == ord('+') or key == ord('='):
            if speed < 100:
                speed += 10
                tello.set_speed(speed)
                print(f"⚡ Скорость увеличена до: {speed}")
                last_action = f"Скорость {speed}"
            else:
                print("⚠ Максимальная скорость (100)")

        # Уменьшение скорости (-)
        elif key == ord('-') or key == ord('_'):
            if speed > 10:
                speed -= 10
                tello.set_speed(speed)
                print(f"⚡ Скорость уменьшена до: {speed}")
                last_action = f"Скорость {speed}"
            else:
                print("⚠ Минимальная скорость (10)")

        # Увеличение дистанции (])
        elif key == ord(']'):
            if distance < 100:
                distance += 10
                print(f"📏 Дистанция увеличена до: {distance}см")
                last_action = f"Дистанция {distance}см"

        # Уменьшение дистанции ([)
        elif key == ord('['):
            if distance > 20:
                distance -= 10
                print(f"📏 Дистанция уменьшена до: {distance}см")
                last_action = f"Дистанция {distance}см"

        # ПЕРЕКЛЮЧАТЕЛИ

        # Пауза/возобновление (пробел)
        elif key == ord(' '):
            paused = not paused
            status = "приостановлен" if paused else "возобновлён"
            print(f"⏸ Видеопоток {status}")
            last_action = f"Пауза {status}"

        # Зеркалирование (f)
        elif key == ord('f'):
            mirror_enabled = not mirror_enabled
            print(f"🔄 Зеркалирование: {'Включено' if mirror_enabled else 'Выключено'}")
            last_action = f"Зеркало {mirror_enabled}"

        # ВЫХОД

        # Выход (q)
        elif key == ord('q'):
            print("\n⏹ Завершение программы...")
            try:
                tello.land()
                print("✓ Дрон приземлился")
            except:
                print("⚠ Ошибка при посадке")
            break

        # Аварийная остановка (ESC)
        elif key == 27:  # ESC
            print("\n⚠ АВАРИЙНАЯ ОСТАНОВКА!")
            try:
                tello.emergency()
                print("✓ Аварийная остановка выполнена")
            except:
                print("⚠ Ошибка аварийной остановки")
            break

        # ОТЛАДКА
        # Если нажата любая другая клавиша
        elif key != 255:  # 255 - ничего не нажато
            print(f"ℹ Неизвестная команда: {chr(key) if 32 <= key <= 126 else key}")

    # ЗАВЕРШЕНИЕ
    print("\n ЗАВЕРШЕНИЕ ")

    # Отключение видеопотока
    try:
        tello.streamoff()
        print("✓ Видеопоток выключен")
    except:
        print("⚠ Ошибка при отключении видеопотока")

    # Закрытие окон
    cv2.destroyAllWindows()
    print("✓ Окна закрыты")

    # Отключение от дрона
    try:
        tello.end()
        print("✓ Соединение закрыто")
    except:
        print("⚠ Ошибка при закрытии соединения")

    print(f"\n📊 Всего обработано кадров: {frame_count}")
    print("✅ Программа завершена")


# ЗАПУСК
if __name__ == "__main__":
    main()