import cv2
import numpy as np
from djitellopy import Tello
import time

# КЛАСС PID-РЕГУЛЯТОРА

class PIDController:
    """
    PID-регулятор для плавного управления.
    """

    def __init__(self, kp=0.3, ki=0.005, kd=0.05, setpoint=0, max_output=30):
        """
        Инициализация PID-регулятора.

        Параметры:
            kp (float): Пропорциональный коэффициент
            ki (float): Интегральный коэффициент
            kd (float): Дифференциальный коэффициент
            setpoint (float): Целевое значение
            max_output (float): Максимальное выходное значение
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.max_output = max_output

        # Переменные состояния
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()

        # Ограничения
        self.integral_limit = max_output * 2
        self.dead_zone = 2  # Мёртвая зона в выходном сигнале

    def update(self, current_value, dt=None):
        """
        Обновление регулятора и вычисление управляющего сигнала.
        """
        # Вычисляем временной шаг
        if dt is None:
            current_time = time.time()
            dt = max(current_time - self.last_time, 0.001)
            self.last_time = current_time

        # Вычисляем ошибку
        error = self.setpoint - current_value

        # Обновляем интегральную составляющую
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)

        # Вычисляем дифференциальную составляющую
        derivative = (error - self.last_error) / dt if dt > 0 else 0

        # Вычисляем выходной сигнал
        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        # Сохраняем ошибку для следующей итерации
        self.last_error = error

        # Применяем мёртвую зону
        if abs(output) < self.dead_zone:
            return 0

        # Ограничиваем выход
        output = np.clip(output, -self.max_output, self.max_output)

        return output

    def reset(self):
        """Сброс состояния регулятора"""
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()

# КЛАСС ДЛЯ УПРАВЛЕНИЯ ДРОНОМ

class DroneController:
    """
    Класс для управления дроном на основе положения лица.
    Объединяет управление по X (поворот), Y (высота) и Z (расстояние).
    """

    def __init__(self, tello):
        """
        Инициализация контроллера.

        Параметры:
            tello (Tello): Объект дрона
        """
        self.tello = tello
        self.is_flying = False

        # PID-регуляторы для разных осей
        # Для поворота (X) - более чувствительный
        self.pid_x = PIDController(
            kp=0.4,          # Пропорциональный
            ki=0.005,        # Интегральный
            kd=0.08,         # Дифференциальный
            setpoint=0,      # Цель: лицо в центре по X
            max_output=30    # Максимальный поворот 30°
        )

        # Для высоты (Y) - менее чувствительный
        self.pid_y = PIDController(
            kp=0.15,         # Пропорциональный
            ki=0.003,        # Интегральный
            kd=0.05,         # Дифференциальный
            setpoint=0,      # Цель: лицо в центре по Y
            max_output=20    # Максимальное движение 20 см
        )

        # Для расстояния (Z) - по площади лица
        self.pid_z = PIDController(
            kp=0.12,         # Пропорциональный
            ki=0.003,        # Интегральный
            kd=0.02,         # Дифференциальный
            setpoint=15000,  # Целевая площадь лица
            max_output=25    # Максимальное движение 25 см
        )

        # Флаги для включения/отключения осей
        self.enable_x = True   # Поворот
        self.enable_y = True   # Высота
        self.enable_z = True   # Расстояние

        # Статистика
        self.stats = {
            'x_error': 0,
            'y_error': 0,
            'z_error': 0,
            'x_output': 0,
            'y_output': 0,
            'z_output': 0
        }

    def takeoff(self):
        """Взлёт дрона"""
        if not self.is_flying:
            self.tello.takeoff()
            time.sleep(0.5)
            self.tello.move_up(30)
            self.is_flying = True
            self.reset()
            print("Взлёт!")
            return True
        return False

    def land(self):
        """Посадка дрона"""
        if self.is_flying:
            self.tello.land()
            self.is_flying = False
            self.tello.send_rc_control(0, 0, 0, 0)
            self.reset()
            print("Посадка!")
            return True
        return False

    def reset(self):
        """Сброс всех PID-регуляторов"""
        self.pid_x.reset()
        self.pid_y.reset()
        self.pid_z.reset()
        print("PID сброшены!")

    def update(self, face_center_x, face_center_y, face_area, frame_width, frame_height):
        """
        Обновление управления на основе положения лица.

        Параметры:
            face_center_x (int): X-координата центра лица
            face_center_y (int): Y-координата центра лица
            face_area (int): Площадь лица (w * h)
            frame_width (int): Ширина кадра
            frame_height (int): Высота кадра
        """
        if not self.is_flying:
            return

        # Центр кадра
        center_x = frame_width // 2
        center_y = frame_height // 2

        # Вычисляем смещения
        offset_x = face_center_x - center_x
        offset_y = face_center_y - center_y

        # Нормализуем смещения (в процентах от размера кадра)
        norm_x = offset_x / (frame_width / 2) * 100  # -100..100
        norm_y = offset_y / (frame_height / 2) * 100  # -100..100

        # Вычисляем управляющие сигналы через PID
        x_output = self.pid_x.update(norm_x) if self.enable_x else 0
        y_output = self.pid_y.update(norm_y) if self.enable_y else 0
        z_output = self.pid_z.update(face_area) if self.enable_z else 0

        # Сохраняем статистику
        self.stats['x_error'] = norm_x
        self.stats['y_error'] = norm_y
        self.stats['z_error'] = self.pid_z.setpoint - face_area
        self.stats['x_output'] = x_output
        self.stats['y_output'] = y_output
        self.stats['z_output'] = z_output

        # Отправляем команды дрону
        self._execute_commands(x_output, y_output, z_output)

        return self.stats

    def _execute_commands(self, x_output, y_output, z_output):
        """
        Выполнение команд управления.

        Параметры:
            x_output (float): Сигнал для поворота (градусы)
            y_output (float): Сигнал для высоты (см)
            z_output (float): Сигнал для расстояния (см)
        """
        # 1. Поворот (X)
        if abs(x_output) > 0.5:
            if x_output > 0:
                # Поворот вправо
                angle = min(abs(x_output), 30)
                self.tello.rotate_clockwise(int(angle))
                print(f"Поворот вправо: {int(angle)}°")
            else:
                # Поворот влево
                angle = min(abs(x_output), 30)
                self.tello.rotate_counter_clockwise(int(angle))
                print(f"Поворот влево: {int(angle)}°")

        # 2. Высота (Y)
        if abs(y_output) > 0.5:
            if y_output > 0:
                # Движение вверх
                distance = min(abs(y_output), 20)
                self.tello.move_up(int(distance))
                print(f"Вверх: {int(distance)} см")
            else:
                # Движение вниз
                distance = min(abs(y_output), 20)
                self.tello.move_down(int(distance))
                print(f"Вниз: {int(distance)} см")

        # 3. Расстояние (Z)
        if abs(z_output) > 0.5:
            if z_output > 0:
                # Движение вперёд
                distance = min(abs(z_output), 25)
                self.tello.move_forward(int(distance))
                print(f"Вперёд: {int(distance)} см")
            else:
                # Движение назад
                distance = min(abs(z_output), 25)
                self.tello.move_back(int(distance))
                print(f"Назад: {int(distance)} см")

        # Если все сигналы нулевые - останавливаемся
        if abs(x_output) < 0.5 and abs(y_output) < 0.5 and abs(z_output) < 0.5:
            self.tello.send_rc_control(0, 0, 0, 0)

    def toggle_axis(self, axis):
        """
        Включение/выключение оси управления.

        Параметры:
            axis (str): 'x', 'y' или 'z'
        """
        if axis == 'x':
            self.enable_x = not self.enable_x
            print(f"{'✅' if self.enable_x else '❌'} Поворот: {self.enable_x}")
        elif axis == 'y':
            self.enable_y = not self.enable_y
            print(f"{'✅' if self.enable_y else '❌'} Высота: {self.enable_y}")
        elif axis == 'z':
            self.enable_z = not self.enable_z
            print(f"{'✅' if self.enable_z else '❌'} Расстояние: {self.enable_z}")

# ОСНОВНАЯ ПРОГРАММА

print("=" * 70)
print("Lab 37 EXTENDED: Full Face Tracking (X + Y + Z + PID)")
print("=" * 70)

# 1. ПОДКЛЮЧЕНИЕ К ДРОНУ

print("\n Подключение к Tello...")
tello = Tello()

try:
    tello.connect()
    print("Подключено к Tello!")
except Exception as e:
    print(f"Ошибка подключения: {e}")
    exit()

# Проверка батареи
battery = tello.get_battery()
print(f"Батарея: {battery}%")

if battery < 15:
    print("Критически низкий заряд батареи!")
    tello.end()
    exit()

# 2. НАСТРОЙКА ВИДЕОПОТОКА

print("\n Запуск видеопотока...")
tello.streamoff()
tello.streamon()
time.sleep(1.5)

frame_read = tello.get_frame_read()

# Проверка получения кадра
test_frame = frame_read.frame
if test_frame is None:
    print("Не удалось получить кадр с дрона!")
    tello.end()
    exit()

print("Видеопоток работает")

# 3. ЗАГРУЗКА МОДЕЛИ ДЕТЕКЦИИ ЛИЦ

print("\n Загрузка каскадного классификатора...")
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

if face_cascade.empty():
    print("Ошибка загрузки классификатора!")
    tello.end()
    exit()

print("Классификатор загружен")

# 4. НАСТРОЙКА КОНСТАНТ

# Параметры кадра
FRAME_WIDTH = 480
FRAME_HEIGHT = 360

# Параметры детекции
MIN_FACE_SIZE = (60, 60)
DETECTION_SCALE = 1.15
MIN_NEIGHBORS = 5

# Визуализация
SHOW_ZONES = True
SHOW_STATS = True

# 5. СОЗДАНИЕ КОНТРОЛЛЕРА

controller = DroneController(tello)

print(f"\n Параметры управления:")
print(f"   Поворот (X): kp={controller.pid_x.kp}, ki={controller.pid_x.ki}, kd={controller.pid_x.kd}")
print(f"   Высота (Y): kp={controller.pid_y.kp}, ki={controller.pid_y.ki}, kd={controller.pid_y.kd}")
print(f"   Расстояние (Z): kp={controller.pid_z.kp}, ki={controller.pid_z.ki}, kd={controller.pid_z.kd}")

# 6. ФУНКЦИИ ВИЗУАЛИЗАЦИИ

def draw_zones(frame, center_x, center_y):
    """Рисует зоны управления на кадре."""
    height, width = frame.shape[:2]

    # Вертикальные зоны (для поворота)
    cv2.line(frame, (center_x - 80, 0), (center_x - 80, height), (0, 0, 255), 1)
    cv2.line(frame, (center_x + 80, 0), (center_x + 80, height), (0, 0, 255), 1)

    # Горизонтальные зоны (для высоты)
    cv2.line(frame, (0, center_y - 60), (width, center_y - 60), (0, 0, 255), 1)
    cv2.line(frame, (0, center_y + 60), (width, center_y + 60), (0, 0, 255), 1)

    # Центральная зона (зелёная)
    cv2.rectangle(frame,
                  (center_x - 80, center_y - 60),
                  (center_x + 80, center_y + 60),
                  (0, 255, 0), 1)

    # Подписи
    cv2.putText(frame, "TURN LEFT", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "TURN RIGHT", (width - 80, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "UP", (width // 2 - 15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "DOWN", (width // 2 - 15, height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "CENTER", (center_x - 30, center_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    return frame


def draw_face_info(frame, face, center_x, center_y, offset_x, offset_y, area):
    """Рисует информацию о лице на кадре."""
    (x, y, w, h) = face

    # Центр лица
    face_cx = x + w // 2
    face_cy = y + h // 2

    # Прямоугольник вокруг лица
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Центр лица (красный круг)
    cv2.circle(frame, (face_cx, face_cy), 8, (0, 0, 255), -1)

    # Линия от центра лица к центру кадра
    cv2.line(frame, (face_cx, face_cy), (center_x, center_y), (255, 0, 0), 2)

    # Информация о смещении
    cv2.putText(frame, f"Offset X: {offset_x:+.0f}px", (x, y - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(frame, f"Offset Y: {offset_y:+.0f}px", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(frame, f"Area: {area}px", (x, y + h + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    return frame

# 7. ОТОБРАЖЕНИЕ ИНСТРУКЦИЙ

print("\n" + "=" * 70)
print("УПРАВЛЕНИЕ:")
print("  [t] Взлёт              [l] Посадка")
print("  [1] Вкл/Выкл поворот   [2] Вкл/Выкл высоту")
print("  [3] Вкл/Выкл расстояние")
print("  [q] Выход              [r] Сброс PID")
print("  [+] Увеличить скорость [-] Уменьшить скорость")
print(" Дрон автоматически следит за лицом во всех осях!\n")

# 8. ОСНОВНОЙ ЦИКЛ

try:
    while True:
        # 8.1. ПОЛУЧЕНИЕ КАДРА
        frame = frame_read.frame

        if frame is None:
            print("Кадр не получен!")
            time.sleep(0.3)
            continue

        # Конвертация RGB -> BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        # 8.2. РАЗМЕРЫ КАДРА
        height, width = frame.shape[:2]
        center_x = width // 2
        center_y = height // 2

        # 8.3. ВИЗУАЛИЗАЦИЯ
        if SHOW_ZONES:
            frame = draw_zones(frame, center_x, center_y)

        # Центр кадра (синий круг)
        cv2.circle(frame, (center_x, center_y), 8, (255, 0, 0), -1)
        cv2.putText(frame, "CENTER", (center_x + 15, center_y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        # 8.4. ДЕТЕКЦИЯ ЛИЦ
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=DETECTION_SCALE,
            minNeighbors=MIN_NEIGHBORS,
            minSize=MIN_FACE_SIZE
        )

        # 8.5. ОБРАБОТКА ЛИЦ
        offset_x = 0
        offset_y = 0
        face_area = 0
        face_found = False

        if len(faces) == 0:
            cv2.putText(frame, "⚠️ NO FACE", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if controller.is_flying:
                tello.send_rc_control(0, 0, 0, 0)
        else:
            # Берём самое большое лицо
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            (x, y, w, h) = largest_face
            face_area = w * h
            face_found = True

            # Центр лица
            face_cx = x + w // 2
            face_cy = y + h // 2

            # Смещения
            offset_x = face_cx - center_x
            offset_y = face_cy - center_y

            # Визуализация
            frame = draw_face_info(frame, largest_face, center_x, center_y,
                                   offset_x, offset_y, face_area)

            # Обновление управления
            stats = controller.update(face_cx, face_cy, face_area, width, height)

        # 8.6. ИНФОРМАЦИЯ НА ЭКРАНЕ
        # Основная информация
        cv2.putText(frame, f"Battery: {tello.get_battery()}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Flying: {'✅' if controller.is_flying else '❌'}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Статус осей
        cv2.putText(frame, f"X: {'ON' if controller.enable_x else 'OFF'}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0) if controller.enable_x else (0, 0, 255), 1)
        cv2.putText(frame, f"Y: {'ON' if controller.enable_y else 'OFF'}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0) if controller.enable_y else (0, 0, 255), 1)
        cv2.putText(frame, f"Z: {'ON' if controller.enable_z else 'OFF'}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0) if controller.enable_z else (0, 0, 255), 1)

        # Статистика PID
        if SHOW_STATS and face_found:
            cv2.putText(frame, f"X err: {stats['x_error']:.1f}%", (width - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(frame, f"X out: {stats['x_output']:.1f}°", (width - 150, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(frame, f"Y err: {stats['y_error']:.1f}%", (width - 150, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(frame, f"Y out: {stats['y_output']:.1f}cm", (width - 150, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(frame, f"Z err: {stats['z_error']:.0f}px", (width - 150, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(frame, f"Z out: {stats['z_output']:.1f}cm", (width - 150, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Количество лиц
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # 8.7. ОТОБРАЖЕНИЕ
        cv2.imshow('Lab 37 EXTENDED: Full Face Tracking', frame)

        # 8.8. УПРАВЛЕНИЕ КЛАВИШАМИ
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Выход...")
            break

        elif key == ord('t'):
            controller.takeoff()

        elif key == ord('l'):
            controller.land()

        elif key == ord('1'):
            controller.toggle_axis('x')

        elif key == ord('2'):
            controller.toggle_axis('y')

        elif key == ord('3'):
            controller.toggle_axis('z')

        elif key == ord('r'):
            controller.reset()

        elif key == ord('+') or key == ord('='):
            # Увеличение скорости (увеличиваем kp)
            controller.pid_x.kp *= 1.2
            controller.pid_y.kp *= 1.2
            controller.pid_z.kp *= 1.2
            print(f"Скорость увеличена: X_kp={controller.pid_x.kp:.2f}")

        elif key == ord('-') or key == ord('_'):
            # Уменьшение скорости (уменьшаем kp)
            controller.pid_x.kp *= 0.8
            controller.pid_y.kp *= 0.8
            controller.pid_z.kp *= 0.8
            print(f"Скорость уменьшена: X_kp={controller.pid_x.kp:.2f}")

except KeyboardInterrupt:
    print("\n Программа прервана пользователем")

# 9. ОЧИСТКА РЕСУРСОВ

finally:
    print("\n Очистка ресурсов...")

    if controller.is_flying:
        print(" Посадка дрона...")
        try:
            tello.land()
            time.sleep(2)
        except:
            pass

    tello.streamoff()
    tello.end()
    cv2.destroyAllWindows()