"""
07. Живой график в реальном времени (PlotModule)
----------------------------------------------------
Часть А: обычный синус — для понимания, как работает LivePlot.
Часть Б: график X-координаты центра обнаруженного лица (требует камеру).

Запустите нужную функцию в конце файла.
"""

import math
import cv2
import cvzone
from cvzone.PlotModule import LivePlot
from cvzone.FaceDetectionModule import FaceDetector


def run_sine_plot():
    sinPlot = LivePlot(w=1200, yLimit=[-100, 100], interval=0.01)
    xSin = 0

    while True:
        xSin += 1
        if xSin == 360:
            xSin = 0

        imgPlotSin = sinPlot.update(int(math.sin(math.radians(xSin)) * 100))
        cv2.imshow("07a - Sine Plot", imgPlotSin)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def run_face_x_plot():
    cap = cv2.VideoCapture(0)
    detector = FaceDetector(minDetectionCon=0.85, modelSelection=0)
    xPlot = LivePlot(w=1200, yLimit=[0, 640], interval=0.01)

    while True:
        success, img = cap.read()
        if not success:
            break

        img, bboxs = detector.findFaces(img, draw=False)
        val = 0
        if bboxs:
            for bbox in bboxs:
                center = bbox["center"]
                x, y, w, h = bbox['bbox']
                score = int(bbox['score'][0] * 100)
                val = center[0]

                cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
                cvzone.putTextRect(img, f'{score}%', (x, y - 10))
                cvzone.cornerRect(img, (x, y, w, h))

        imgPlot = xPlot.update(val)

        cv2.imshow("07b - Face X Plot", imgPlot)
        cv2.imshow("Камера", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_sine_plot()
    # run_face_x_plot()
