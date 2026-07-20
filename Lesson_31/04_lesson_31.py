"""
04. Детекция лиц (FaceDetectionModule)
-----------------------------------------
Находит лица через веб-камеру, рисует рамку и показывает
уверенность (confidence) детекции в процентах.
"""

import cvzone
from cvzone.FaceDetectionModule import FaceDetector
import cv2

cap = cv2.VideoCapture(0)

# minDetectionCon — минимальная уверенность (0..1)
# modelSelection: 0 — лица до 2 метров, 1 — лица до 5 метров
detector = FaceDetector(minDetectionCon=0.5, modelSelection=0)

while True:
    success, img = cap.read()
    if not success:
        break

    img, bboxs = detector.findFaces(img, draw=False)

    if bboxs:
        for bbox in bboxs:
            center = bbox["center"]
            x, y, w, h = bbox['bbox']
            score = int(bbox['score'][0] * 100)

            cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
            cvzone.putTextRect(img, f'{score}%', (x, y - 10))
            cvzone.cornerRect(img, (x, y, w, h))

    cv2.imshow("04 - Face Detection", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
