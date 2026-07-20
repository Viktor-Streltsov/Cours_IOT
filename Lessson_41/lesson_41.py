from djitellopy import Tello
import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector
from cvzone.PIDModule import PID
from cvzone.PlotModule import LivePlot
import time

print("=" * 70)
print("Lab 41: Face Tracking Drone with PID Control (cvzone)")
print("=" * 70)

print("\nConnecting to Tello...")
me = Tello()

try:
    me.connect()
    print("Connected to Tello")
except Exception as e:
    print(f"Connection error: {e}")
    exit()

battery = me.get_battery()
print(f"Battery: {battery}%")

if battery < 15:
    print("Low battery!")
    me.end()
    exit()

print("\nStarting video stream...")
me.streamoff()
me.streamon()
time.sleep(1.5)

print("Initializing Face Detector...")
detector = FaceDetector(minDetectionCon=0.5)

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Настройка PID-регуляторов
# Для поворота (X) - более чувствительный
xPID = PID([0.22, 0, 0.1], FRAME_WIDTH // 2)
# Для высоты (Y)
yPID = PID([0.27, 0, 0.1], FRAME_HEIGHT // 2, axis=1)
# Для расстояния (Z)
zPID = PID([0.005, 0, 0.003], 12000, limit=[-20, 15])

# Графики для визуализации
myPlotX = LivePlot(yLimit=[-100, 100], char='X')
myPlotY = LivePlot(yLimit=[-100, 100], char='Y')
myPlotZ = LivePlot(yLimit=[-100, 100], char='Z')

is_flying = False


def draw_face_info(img, bboxs):
    """Рисует дополнительную информацию о лице."""
    if bboxs:
        cx, cy = bboxs[0]['center']
        x, y, w, h = bboxs[0]['bbox']
        area = w * h

        cv2.putText(img, f"Area: {area}px", (10, 50),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 255), 2)
        cv2.putText(img, f"Center: ({cx}, {cy})", (10, 80),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 255), 2)

        return area, cx, cy
    return 0, 0, 0


print("\n" + "=" * 70)
print("CONTROLS:")
print("=" * 70)
print("  [t] Takeoff              [l] Land")
print("  [q] Exit")
print("=" * 70)
print("Drone automatically tracks face using PID control")
print("X PID: P=0.22, I=0, D=0.1")
print("Y PID: P=0.27, I=0, D=0.1")
print("Z PID: P=0.005, I=0, D=0.003")
print("\nGraphs show PID output values in real time\n")

try:
    while True:
        # Получение кадра
        img = me.get_frame_read().frame
        if img is None:
            print("No frame received!")
            time.sleep(0.3)
            continue

        img = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))

        # Детекция лиц
        img, bboxs = detector.findFaces(img, draw=True)

        xVal = 0
        yVal = 0
        zVal = 0
        area = 0

        if bboxs:
            # Получение данных о лице
            cx, cy = bboxs[0]['center']
            x, y, w, h = bboxs[0]['bbox']
            area = w * h

            # Вычисление PID-выходов
            xVal = int(xPID.update(cx))
            yVal = int(yPID.update(cy))
            zVal = int(zPID.update(area))

            # Обновление графиков
            imgPlotX = myPlotX.update(xVal)
            imgPlotY = myPlotY.update(yVal)
            imgPlotZ = myPlotZ.update(zVal)

            # Отрисовка PID-информации на изображении
            img = xPID.draw(img, [cx, cy])
            img = yPID.draw(img, [cx, cy])
            img = zPID.draw(img, [cx, cy])

            # Стэкинг изображений (оригинал + 3 графика)
            imgStacked = cvzone.stackImages(
                [img, imgPlotX, imgPlotY, imgPlotZ],
                2, 0.75
            )

            # Отображение площади
            cv2.putText(imgStacked, f"Area: {area}", (20, 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)
            cv2.putText(imgStacked, f"PID X: {xVal}", (20, 90),
                        cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 0), 2)
            cv2.putText(imgStacked, f"PID Y: {yVal}", (20, 120),
                        cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 0), 2)
            cv2.putText(imgStacked, f"PID Z: {zVal}", (20, 150),
                        cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 0), 2)

            # Управление дроном
            if is_flying:
                # send_rc_control(left_right, forward_backward, up_down, yaw)
                # xVal: поворот (yaw)
                # yVal: высота (up_down) - инвертировано
                # zVal: расстояние (forward_backward) - инвертировано
                me.send_rc_control(0, -zVal, -yVal, xVal)
                print(f"X: {xVal:+3d}, Y: {yVal:+3d}, Z: {zVal:+3d}")
        else:
            # Если лицо не найдено - останавливаемся
            if is_flying:
                me.send_rc_control(0, 0, 0, 0)

            imgStacked = cvzone.stackImages([img], 1, 0.75)
            cv2.putText(imgStacked, "NO FACE", (20, 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)

        # Информация о состоянии
        cv2.putText(imgStacked, f"Flying: {is_flying}", (FRAME_WIDTH - 150, 30),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0) if is_flying else (0, 0, 255), 2)
        cv2.putText(imgStacked, f"Battery: {me.get_battery()}%", (FRAME_WIDTH - 150, 60),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

        cv2.imshow("Lab 41: PID Face Tracking", imgStacked)

        key = cv2.waitKey(5) & 0xFF

        if key == ord('q'):
            print("Exit")
            break

        elif key == ord('t'):
            if not is_flying:
                print("Takeoff")
                me.takeoff()
                time.sleep(0.5)
                me.move_up(30)
                is_flying = True
            else:
                print("Already flying")

        elif key == ord('l'):
            if is_flying:
                print("Land")
                me.land()
                is_flying = False
                me.send_rc_control(0, 0, 0, 0)
            else:
                print("Already on ground")

except KeyboardInterrupt:
    print("\nInterrupted")

finally:
    print("\nCleaning up...")

    if is_flying:
        print("Landing...")
        try:
            me.land()
            time.sleep(2)
        except:
            pass

    me.streamoff()
    me.end()
    cv2.destroyAllWindows()
    print("Done")