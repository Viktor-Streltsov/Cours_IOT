"""
05. Сетка лица (FaceMesh) и замена фона (Selfie Segmentation)
------------------------------------------------------------------
Часть А: FaceMeshDetector — 468 точек лица, пример расчёта расстояния
         между точками (можно использовать для детекции моргания).
Часть Б: SelfiSegmentation — замена фона за человеком одним цветом
         или другим изображением.

Запустите нужную функцию в конце файла.
"""

import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.SelfiSegmentationModule import SelfiSegmentation


def run_face_mesh():
    cap = cv2.VideoCapture(0)
    detector = FaceMeshDetector(staticMode=False, maxFaces=2,
                                 minDetectionCon=0.5, minTrackCon=0.5)

    while True:
        success, img = cap.read()
        if not success:
            break

        img, faces = detector.findFaceMesh(img, draw=True)

        if faces:
            face = faces[0]
            # Точки над и под левым глазом — удобно для детекции моргания
            leftEyeUpPoint = face[159]
            leftEyeDownPoint = face[23]

            distance, info = detector.findDistance(leftEyeUpPoint, leftEyeDownPoint)
            print(f"Расстояние между веками: {distance:.1f}")

        cv2.imshow("05a - Face Mesh", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def run_selfie_segmentation():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    # model: 0 — общий режим, 1 — режим для пейзажа (быстрее)
    segmentor = SelfiSegmentation(model=0)

    while True:
        success, img = cap.read()
        if not success:
            break

        # Заменяем фон на однотонный цвет (можно передать своё изображение
        # такого же размера вместо цвета)
        imgOut = segmentor.removeBG(img, imgBg=(255, 0, 255), cutThreshold=0.1)

        imgStacked = cvzone.stackImages([img, imgOut], cols=2, scale=1)
        cv2.imshow("05b - Selfie Segmentation", imgStacked)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_face_mesh()
    # run_selfie_segmentation()
