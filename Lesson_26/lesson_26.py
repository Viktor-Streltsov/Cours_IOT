import cv2

# 1. ЗАГРУЗКА КЛАССИФИКАТОРОВ С ПРОВЕРКОЙ
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# Проверяем, загрузились ли классификаторы
if face_cascade.empty():
    print("ОШИБКА: Не найден файл haarcascade_frontalface_default.xml")
    exit()
if eye_cascade.empty():
    print("ОШИБКА: Не найден файл haarcascade_eye.xml")
    exit()

# 2. ЗАГРУЗКА ИЗОБРАЖЕНИЯ С ПРОВЕРКОЙ
img = cv2.imread('img.png')
if img is None:
    print("ОШИБКА: Файл test3.jpg не найден или не может быть прочитан")
    exit()

# 3. ПРЕОБРАЗОВАНИЕ В ОТТЕНКИ СЕРОГО
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 4. ДЕТЕКЦИЯ ЛИЦ
# Параметры:
# scaleFactor=1.1 - более точный поиск (медленнее, но меньше пропусков)
# minNeighbors=5 - количество соседних прямоугольников для подтверждения
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

# Проверяем, найдены ли лица
if len(faces) == 0:
    print("Лица на изображении не обнаружены")
else:
    print(f"Найдено лиц: {len(faces)}")

# 5. ОБРАБОТКА КАЖДОГО НАЙДЕННОГО ЛИЦА
for (x, y, w, h) in faces:
    # Рисуем прямоугольник вокруг лица (синий)
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Добавляем подпись "Face"
    cv2.putText(img, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Создаем ROI (область интереса) - только область лица
    roi_gray = gray[y:y + h, x:x + w]
    roi_color = img[y:y + h, x:x + w]

    # 6. ДЕТЕКЦИЯ ГЛАЗ ВНУТРИ ОБЛАСТИ ЛИЦА
    # Увеличиваем minNeighbors для глаз, чтобы уменьшить ложные срабатывания
    eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15))

    # Рисуем прямоугольники вокруг глаз (зеленые)
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        # Можно добавить подпись "Eye" (опционально)
        cv2.putText(roi_color, "Eye", (ex, ey - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Выводим количество найденных глаз для каждого лица
    print(f"Для лица ({x}, {y}, {w}, {h}) найдено глаз: {len(eyes)}")

# 7. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА
cv2.imshow('Face and Eye Detection', img)
cv2.waitKey(0)  # Ожидание нажатия любой клавиши
cv2.destroyAllWindows()

# 8. СОХРАНЕНИЕ РЕЗУЛЬТАТА (опционально)
cv2.imwrite('result_with_faces_and_eyes.jpg', img)
print("Результат сохранен в файл result_with_faces_and_eyes.jpg")