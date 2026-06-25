import cv2

cap = cv2.VideoCapture(0)
w, h = int(cap.get(3)), int(cap.get(4))
# Используем расширение .mp4 для кодека mp4v
out = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (w, h))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    out.write(frame)
    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()