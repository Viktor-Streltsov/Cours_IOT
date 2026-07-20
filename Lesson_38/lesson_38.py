import cv2
from djitellopy import Tello
import time

print("=" * 70)
print("Lab 38: Up/Down Control (Face Height Tracking)")
print("=" * 70)

print("\nConnecting to Tello...")
tello = Tello()

try:
    tello.connect()
    print("Connected to Tello")
except Exception as e:
    print(f"Connection error: {e}")
    exit()

battery = tello.get_battery()
print(f"Battery: {battery}%")

if battery < 15:
    print("Low battery!")
    tello.end()
    exit()

print("\nStarting video stream...")
tello.streamoff()
tello.streamon()
time.sleep(1.5)

frame_read = tello.get_frame_read()

test_frame = frame_read.frame
if test_frame is None:
    print("Failed to get frame from drone!")
    tello.end()
    exit()

print("Video stream is working")

print("\nLoading face cascade classifier...")
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

if face_cascade.empty():
    print("Failed to load classifier!")
    tello.end()
    exit()

print("Classifier loaded")

FRAME_WIDTH = 480
FRAME_HEIGHT = 360

MIN_FACE_SIZE = (50, 50)
DETECTION_SCALE = 1.15
MIN_NEIGHBORS = 5

MOVE_STEP = 20
DEAD_ZONE_X = 70
DEAD_ZONE_Y = 70
Y_OFFSET = 30

is_flying = False


def adjust_tello_position_x(offset_x):
    """
    Управление поворотом дрона на основе смещения лица по X.
    """
    global is_flying

    if not is_flying:
        return

    if offset_x == 0:
        return

    if abs(offset_x) < DEAD_ZONE_X:
        return

    if offset_x < 0:
        tello.rotate_counter_clockwise(10)
        print(f"Rotate left: {offset_x}px")
    else:
        tello.rotate_clockwise(10)
        print(f"Rotate right: {offset_x}px")


def adjust_tello_position_y(offset_y):
    """
    Управление высотой дрона на основе смещения лица по Y.
    Смещение -30 позволяет лицу быть чуть выше центра для лучшего кадрирования.
    """
    global is_flying

    if not is_flying:
        return

    adjusted_offset = offset_y - Y_OFFSET

    if abs(adjusted_offset) < DEAD_ZONE_Y:
        return

    if adjusted_offset < 0:
        tello.move_up(MOVE_STEP)
        print(f"Move up: {adjusted_offset}px")
    else:
        tello.move_down(MOVE_STEP)
        print(f"Move down: {adjusted_offset}px")


def draw_face_info(frame, face, center_x, center_y, offset_x, offset_y):
    """Рисует информацию о лице на кадре."""
    (x, y, w, h) = face

    face_cx = x + w // 2
    face_cy = y + h // 2

    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.circle(frame, (face_cx, face_cy), 8, (0, 0, 255), -1)
    cv2.line(frame, (face_cx, face_cy), (center_x, center_y), (255, 0, 0), 2)

    cv2.putText(frame, f"Offset X: {offset_x:+.0f}px", (x, y - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(frame, f"Offset Y: {offset_y:+.0f}px", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    adjusted_y = offset_y - Y_OFFSET
    if abs(adjusted_y) > DEAD_ZONE_Y:
        if adjusted_y < 0:
            cv2.putText(frame, "MOVE UP", (x, y + h + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "MOVE DOWN", (x, y + h + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "CENTER Y", (x, y + h + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame


def draw_zones(frame, center_x, center_y):
    """Рисует зоны управления на кадре."""
    height, width = frame.shape[:2]

    cv2.line(frame, (0, center_y - DEAD_ZONE_Y - Y_OFFSET),
             (width, center_y - DEAD_ZONE_Y - Y_OFFSET), (0, 0, 255), 1)
    cv2.line(frame, (0, center_y + DEAD_ZONE_Y - Y_OFFSET),
             (width, center_y + DEAD_ZONE_Y - Y_OFFSET), (0, 0, 255), 1)

    cv2.line(frame, (center_x - DEAD_ZONE_X, 0),
             (center_x - DEAD_ZONE_X, height), (0, 0, 255), 1)
    cv2.line(frame, (center_x + DEAD_ZONE_X, 0),
             (center_x + DEAD_ZONE_X, height), (0, 0, 255), 1)

    cv2.rectangle(frame,
                  (center_x - DEAD_ZONE_X, center_y - DEAD_ZONE_Y - Y_OFFSET),
                  (center_x + DEAD_ZONE_X, center_y + DEAD_ZONE_Y - Y_OFFSET),
                  (0, 255, 0), 1)

    cv2.putText(frame, "TURN LEFT", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "TURN RIGHT", (width - 80, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "UP", (width // 2 - 15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "DOWN", (width // 2 - 15, height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, "CENTER", (center_x - 30, center_y - Y_OFFSET + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    cv2.putText(frame, f"Y OFFSET: {Y_OFFSET}px", (10, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    return frame


def change_y_offset(delta):
    """Изменяет Y_OFFSET на указанное значение."""
    global Y_OFFSET
    Y_OFFSET += delta
    print(f"Y offset: {Y_OFFSET}px")


print("\n" + "=" * 70)
print("CONTROLS:")
print("=" * 70)
print("  [t] Takeoff              [l] Land")
print("  [u] Move up (manual)     [d] Move down (manual)")
print("  [+/-] Change Y offset")
print("  [q] Exit")
print("=" * 70)
print("Drone automatically tracks face vertically (Y axis)")
print(f"Y offset: {Y_OFFSET}px (adjust for better framing)\n")

try:
    while True:
        frame = frame_read.frame

        if frame is None:
            print("No frame received!")
            time.sleep(0.3)
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        height, width = frame.shape[:2]
        center_x = width // 2
        center_y = height // 2

        frame = draw_zones(frame, center_x, center_y)

        cv2.circle(frame, (center_x, center_y), 8, (255, 0, 0), -1)
        cv2.putText(frame, "CENTER", (center_x + 15, center_y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=DETECTION_SCALE,
            minNeighbors=MIN_NEIGHBORS,
            minSize=MIN_FACE_SIZE
        )

        offset_x = 0
        offset_y = 0

        if len(faces) == 0:
            cv2.putText(frame, "NO FACE", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if is_flying:
                tello.send_rc_control(0, 0, 0, 0)
        else:
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            (x, y, w, h) = largest_face

            face_cx = x + w // 2
            face_cy = y + h // 2

            offset_x = face_cx - center_x
            offset_y = face_cy - center_y

            frame = draw_face_info(frame, largest_face, center_x, center_y,
                                   offset_x, offset_y)

            adjust_tello_position_x(offset_x)
            adjust_tello_position_y(offset_y)

        cv2.putText(frame, f"Battery: {tello.get_battery()}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Flying: {is_flying}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame, f"Offset X: {offset_x:+.0f}px", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Offset Y: {offset_y:+.0f}px", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Y Adj: {offset_y - Y_OFFSET:+.0f}px", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        cv2.imshow('Lab 38: Up/Down Control', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Exit")
            break

        elif key == ord('t'):
            if not is_flying:
                tello.takeoff()
                time.sleep(0.5)
                tello.move_up(30)
                is_flying = True
                print("Takeoff")
            else:
                print("Already flying")

        elif key == ord('l'):
            if is_flying:
                tello.land()
                is_flying = False
                tello.send_rc_control(0, 0, 0, 0)
                print("Land")
            else:
                print("Already on ground")

        elif key == ord('u'):
            if is_flying:
                tello.move_up(MOVE_STEP)
                print(f"Move up: {MOVE_STEP}cm (manual)")
            else:
                print("Not flying")

        elif key == ord('d'):
            if is_flying:
                tello.move_down(MOVE_STEP)
                print(f"Move down: {MOVE_STEP}cm (manual)")
            else:
                print("Not flying")

        elif key == ord('+') or key == ord('='):
            change_y_offset(5)

        elif key == ord('-') or key == ord('_'):
            change_y_offset(-5)

except KeyboardInterrupt:
    print("\nInterrupted")

finally:
    print("\nCleaning up...")

    if is_flying:
        print("Landing...")
        try:
            tello.land()
            time.sleep(2)
        except:
            pass

    tello.streamoff()
    tello.end()
    cv2.destroyAllWindows()
    print("Done")