"""
06. Трекинг рук и трекинг позы тела
--------------------------------------
Часть А: HandDetector — определение ключевых точек руки, счёт поднятых
         пальцев, расстояние между пальцами (можно управлять громкостью и т.п.)
Часть Б: PoseDetector — 33 точки тела, расчёт угла в суставе (можно
         использовать для подсчёта приседаний/отжиманий).

Запустите нужную функцию в конце файла.
"""

import cvzone
from cvzone.HandTrackingModule import HandDetector
from cvzone.PoseModule import PoseDetector
import cv2


def run_hand_tracking():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1,
                             detectionCon=0.5, minTrackCon=0.5)

    while True:
        success, img = cap.read()
        if not success:
            break

        hands, img = detector.findHands(img, draw=True, flipType=True)

        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]
            handType1 = hand1["type"]

            fingers1 = detector.fingersUp(hand1)
            print(f'{handType1} рука: поднято пальцев = {fingers1.count(1)}')

            # Расстояние между указательным и средним пальцем
            length, info, img = detector.findDistance(
                lmList1[8][0:2], lmList1[12][0:2], img,
                color=(255, 0, 255), scale=10
            )

        cv2.imshow("06a - Hand Tracking", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def run_pose_detection():
    cap = cv2.VideoCapture(0)
    detector = PoseDetector(staticMode=False, modelComplexity=1,
                             smoothLandmarks=True, enableSegmentation=False,
                             smoothSegmentation=True, detectionCon=0.5, trackCon=0.5)

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.findPose(img)
        lmList, bboxInfo = detector.findPosition(img, draw=True, bboxWithHands=False)

        if lmList:
            center = bboxInfo["center"]
            cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

            # Угол в локтевом суставе (точки плечо-локоть-запястье)
            angle, img = detector.findAngle(
                lmList[11][0:2], lmList[13][0:2], lmList[15][0:2],
                img=img, color=(0, 0, 255), scale=10
            )

            isCloseAngle50 = detector.angleCheck(myAngle=angle, targetAngle=50, offset=10)
            print(f"Угол ~50 градусов: {isCloseAngle50}")

        cv2.imshow("06b - Pose Detection", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_hand_tracking()
    # run_pose_detection()
