# Работа с камерой

import cv2

cap = cv2.VideoCapture(0)  # Открыть камеру

while True:
    ret, frame = cap.read()  # Читать кадр
    if not ret: 
        break
    
    cv2.imshow('Camera', frame)  # Показать кадр
    
    # Выход по ESC, задержка для плавности
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()  # Освободить камеру
cv2.destroyAllWindows()  # Закрыть окна