import cv2

# Загрузка изображения с проверкой
src = cv2.imread('img.png')
if src is None:
    print("Ошибка: Файл 'LenaRGB.bmp' не найден.")
    exit()

# Загрузка классификатора
classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
if classifier.empty():
    print("Ошибка: Не удалось загрузить haarcascade_frontalface_default.xml")
    exit()

# Детекция (лучше переводить в серый)
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

# Рисование прямоугольников (ИСПРАВЛЕННЫЙ СИНТАКСИС)
for (x, y, w, h) in faces:
    cv2.rectangle(src, (x, y), (x + w, y + h), (255, 0, 255), 2)

# Вывод результата
cv2.imshow('Face Detection - Image', src)
cv2.waitKey(0)
cv2.destroyAllWindows()