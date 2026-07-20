import cv2
import numpy as np
from djitellopy import Tello
import time


# КЛАСС PID-РЕГУЛЯТОРА

class PIDController:
    """
    PID-регулятор для плавного управления дроном.

    Позволяет избежать резких движений и обеспечивает
    плавное приближение к целевой позиции.
    """

    def __init__(self, kp=0.15, ki=0.005, kd=0.02, setpoint=15000):
        """
        Инициализация PID-регулятора.

        Параметры:
            kp (float): Пропорциональный коэффициент (основной)
            ki (float): Интегральный коэффициент (устранение ошибки)
            kd (float): Дифференциальный коэффициент (подавление колебаний)
            setpoint (float): Целевое значение (желаемая площадь лица)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        # Переменные состояния
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()

        # Ограничение интегральной составляющей
        self.integral_limit = 5000

        # Минимальное изменение для движения (мёртвая зона)
        self.dead_zone = 500

        # Максимальное движение за один шаг
        self.max_move = 30

    def update(self, current_value, dt=None):
        """
        Обновление регулятора и вычисление управляющего сигнала.

        Параметры:
            current_value (float): Текущее значение (площадь лица)
            dt (float, optional): Временной шаг

        Возвращает:
            float: Сигнал управления (положительный = вперёд, отрицательный = назад)
        """
        # Вычисляем временной шаг
        if dt is None:
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time

            # Защита от слишком маленького dt
            if dt < 0.001:
                dt = 0.001

        # Вычисляем ошибку
        error = self.setpoint - current_value

        # Обновляем интегральную составляющую
        self.integral += error * dt

        # Ограничиваем интегральную составляющую
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

        # Ограничиваем максимальное движение
        output = np.clip(output, -self.max_move, self.max_move)

        return output

    def reset(self):
        """Сброс состояния регулятора"""
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()

    def set_setpoint(self, value):
        """Изменение целевого значения"""
        self.setpoint = value

# ОСНОВНАЯ ПРОГРАММА

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
elif battery < 25:
    print("Низкий заряд батареи. Будьте осторожны!")

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

# Параметры PID-регулятора
# kp: основной коэффициент (чем больше, тем быстрее реакция)
# ki: интегральный (устраняет ошибку)
# kd: дифференциальный (сглаживает колебания)
TARGET_AREA = 15000  # Целевая площадь лица
PID_KP = 0.12
PID_KI = 0.003
PID_KD = 0.02

# Параметры движения
MAX_MOVE = 25  # Максимальное движение (см)
MIN_MOVE = 5  # Минимальное движение (см)
DEAD_ZONE_AREA = 1500  # Мёртвая зона (не реагировать на малые изменения)

# Параметры детекции
MIN_FACE_SIZE = (60, 60)  # Минимальный размер лица
DETECTION_SCALE = 1.15  # Масштаб детекции
MIN_NEIGHBORS = 5  # Количество соседей

# Состояния
is_flying = False

# 5. СОЗДАНИЕ PID-РЕГУЛЯТОРА

pid = PIDController(
    kp=PID_KP,
    ki=PID_KI,
    kd=PID_KD,
    setpoint=TARGET_AREA
)

print(f"\n⚙ Параметры PID:")
print(f"Целевая площадь: {TARGET_AREA} px")
print(f"kp: {PID_KP}, ki: {PID_KI}, kd: {PID_KD}")
print(f"Макс. движение: {MAX_MOVE} см")

# 6. ФУНКЦИИ УПРАВЛЕНИЯ

def adjust_tello_position(area):
    """
    Управление дроном на основе площади лица с использованием PID.

    Параметры:
        area (int): Площадь bounding box лица (w * h)
    """
    global is_flying

    if not is_flying:
        return

    if area == 0:
        # Лицо не найдено - останавливаемся
        tello.send_rc_control(0, 0, 0, 0)
        return

    # Вычисляем управляющий сигнал через PID
    pid_output = pid.update(area)

    # Преобразуем PID выход в движение
    if abs(pid_output) > MIN_MOVE:
        if pid_output > 0:
            # Положительное значение -> двигаемся вперёд
            move_distance = min(pid_output, MAX_MOVE)
            print(f"Вперёд: {move_distance:.1f} см (area={area})")
            tello.move_forward(int(move_distance))
        else:
            # Отрицательное значение -> двигаемся назад
            move_distance = min(abs(pid_output), MAX_MOVE)
            print(f"Назад: {move_distance:.1f} см (area={area})")
            tello.move_back(int(move_distance))
    else:
        # Дрон в целевой зоне
        tello.send_rc_control(0, 0, 0, 0)
        if abs(area - TARGET_AREA) < 500:
            print(f"ИДЕАЛЬНО: area={area}")


def draw_face_info(frame, face, center_x, center_y, area):
    """
    Визуализация информации о лице на кадре.
    """
    (x, y, w, h) = face

    # Центр лица
    face_cx = x + w // 2
    face_cy = y + h // 2

    # 1. Прямоугольник вокруг лица
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 2. Центр лица (красный круг)
    cv2.circle(frame, (face_cx, face_cy), 8, (0, 0, 255), -1)

    # 3. Линия к центру кадра
    cv2.line(frame, (face_cx, face_cy), (center_x, center_y), (255, 0, 0), 2)

    # 4. Информация о площади
    cv2.putText(frame, f"Area: {area}px", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 5. Размеры
    cv2.putText(frame, f"Size: {w}x{h}", (x, y + h + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # 6. Координаты
    cv2.putText(frame, f"({face_cx}, {face_cy})", (x, y + h + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # 7. Индикатор отклонения от цели
    deviation = area - TARGET_AREA
    if abs(deviation) < DEAD_ZONE_AREA:
        status = "PERFECT"
        color = (0, 255, 0)
    elif deviation > 0:
        status = "TOO CLOSE"
        color = (0, 0, 255)
    else:
        status = "TOO FAR"
        color = (0, 0, 255)

    cv2.putText(frame, status, (x, y + h + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return frame

# 7. ОТОБРАЖЕНИЕ ИНСТРУКЦИЙ

print("\n" + "=" * 60)
print("УПРАВЛЕНИЕ:")
print("=" * 60)
print("  [t] Взлёт                    [l] Посадка")
print("  [f] Вперёд (ручной)          [b] Назад (ручной)")
print("  [u] Вверх (ручной)           [d] Вниз (ручной)")
print("  [r] Сброс PID-регулятора")
print("  [+]/[-] Изменить целевую площадь")
print("  [q] Выход")
print("=" * 60)
print("\n Дрон автоматически регулирует расстояние до лица!\n")

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

        # 8.3. ДЕТЕКЦИЯ ЛИЦ
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=DETECTION_SCALE,
            minNeighbors=MIN_NEIGHBORS,
            minSize=MIN_FACE_SIZE
        )

        # 8.4. ВИЗУАЛИЗАЦИЯ ЦЕНТРА КАДРА
        # Центр кадра
        cv2.circle(frame, (center_x, center_y), 10, (255, 0, 0), -1)
        cv2.putText(frame, "FRAME CENTER", (center_x + 15, center_y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        # Целевая зона (круг)
        target_radius = 80
        cv2.circle(frame, (center_x, center_y), target_radius, (0, 255, 0), 1)

        # 8.5. ОБРАБОТКА ЛИЦ
        z_area = 0

        if len(faces) == 0:
            cv2.putText(frame, "⚠️ NO FACE", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if is_flying:
                # Останавливаем движение при потере лица
                tello.send_rc_control(0, 0, 0, 0)
                pid.reset()
        else:
            # Берём самое большое лицо
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            (x, y, w, h) = largest_face
            z_area = w * h

            # Рисуем информацию о лице
            frame = draw_face_info(frame, largest_face, center_x, center_y, z_area)

            # Управляем дроном
            adjust_tello_position(z_area)

        # 8.6. ИНФОРМАЦИЯ НА ЭКРАНЕ
        # Батарея
        cv2.putText(frame, f"Battery: {tello.get_battery()}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Статус полёта
        cv2.putText(frame, f"Flying: {'✅' if is_flying else '❌'}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # PID информация
        if z_area > 0:
            error = TARGET_AREA - z_area
            cv2.putText(frame, f"Error: {error:.0f} px", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Целевая площадь
        cv2.putText(frame, f"Target: {TARGET_AREA} px", (10, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Количество обнаруженных лиц
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # PID параметры
        cv2.putText(frame, f"PID: kp={PID_KP:.2f} ki={PID_KI:.3f} kd={PID_KD:.2f}", (10, 155),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        # 8.7. ОТОБРАЖЕНИЕ
        cv2.imshow('Lab 36: PID Face Distance Control', frame)

        # 8.8. УПРАВЛЕНИЕ КЛАВИШАМИ
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Выход...")
            break

        elif key == ord('t'):
            if not is_flying:
                print("Взлёт!")
                tello.takeoff()
                time.sleep(0.5)
                tello.move_up(30)
                is_flying = True
                pid.reset()
            else:
                print("Дрон уже в воздухе!")

        elif key == ord('l'):
            if is_flying:
                print("Посадка!")
                tello.land()
                is_flying = False
                tello.send_rc_control(0, 0, 0, 0)
                pid.reset()
            else:
                print("Дрон уже на земле!")

        elif key == ord('f'):
            if is_flying:
                tello.move_forward(20)
                print("Вперёд (ручной)")

        elif key == ord('b'):
            if is_flying:
                tello.move_back(20)
                print("Назад (ручной)")

        elif key == ord('u'):
            if is_flying:
                tello.move_up(20)
                print("Вверх (ручной)")

        elif key == ord('d'):
            if is_flying:
                tello.move_down(20)
                print("Вниз (ручной)")

        elif key == ord('r'):
            # Сброс PID
            pid.reset()
            print("PID сброшен!")

        elif key == ord('+') or key == ord('='):
            # Увеличение целевой площади
            TARGET_AREA = min(TARGET_AREA + 1000, 30000)
            pid.set_setpoint(TARGET_AREA)
            print(f"Целевая площадь: {TARGET_AREA} px")

        elif key == ord('-') or key == ord('_'):
            # Уменьшение целевой площади
            TARGET_AREA = max(TARGET_AREA - 1000, 5000)
            pid.set_setpoint(TARGET_AREA)
            print(f"Целевая площадь: {TARGET_AREA} px")

except KeyboardInterrupt:
    print("\n Программа прервана пользователем")

# 9. ОЧИСТКА РЕСУРСОВ

finally:
    print("\n Очистка ресурсов...")

    if is_flying:
        print("Посадка дрона...")
        try:
            tello.land()
            time.sleep(2)
        except:
            pass

    tello.streamoff()
    tello.end()
    cv2.destroyAllWindows()