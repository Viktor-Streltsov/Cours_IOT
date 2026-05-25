import cv2

# Загружаем изображение в оттенках серого
img = cv2.imread('img/drone.jpg', cv2.IMREAD_GRAYSCALE)

# Проверка загрузки
if img is None:
    print("Фаил не найден")
    exit()

# ESC → выход без сохранения
print("ESC - выйти | s - сохранить")

# Отображение
cv2.imshow('image', img)

k = cv2.waitKey(0) & 0xFF

if k == 27:
    cv2.destroyAllWindows()

# 's' → сохранить изображение
elif k == ord('s'):
    cv2.imwrite('opencv_gray.jpg', img)
    print("Изображение схранено")
    cv2.destroyAllWindows()
