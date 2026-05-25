# Подключаем библиотеку OpenCV
import cv2

# Путь к изображению
img_file = "img/drone.jpg"

# Загрузка изображения

# Загружаем цветное изображение
color_img = cv2.imread(img_file, cv2.IMREAD_COLOR)

# Загружаем изображение в оттенках серого
gray_img = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)

# Загружаем изображение без изменений
unchanged_img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

# Проверка загрузки файла

# Если файл не найден — завершаем программу
if color_img is None:
    print("Ошибка: изображение не найдено")
    exit()

# Получение размеров изображения
# shape возвращает:
# (высота, ширина, каналы)

height, width, channels = color_img.shape

# Вывод информации
print("Размеры цветного изображения:")
print(f"Высота: {height} px")
print(f"Ширина: {width} px")
print(f"Каналы: {channels}")

# Для grayscale изображения каналов нет
gray_height, gray_width = gray_img.shape

print("\nРазмеры серого изображения:")
print(f"Высота: {gray_height} px")
print(f"Ширина: {gray_width} px")

# Создание изменяемых окон

# WINDOW_NORMAL позволяет изменять размер окна
cv2.namedWindow("Original Color", cv2.WINDOW_NORMAL)
cv2.namedWindow("Gray Image", cv2.WINDOW_NORMAL)
cv2.namedWindow("Unchanged Image", cv2.WINDOW_NORMAL)

# Изменение размеров окон

# resizeWindow(название, ширина, высота)
cv2.resizeWindow("Original Color", 600, 400)
cv2.resizeWindow("Gray Image", 500, 400)
cv2.resizeWindow("Unchanged Image", 600, 400)

# Отображение изображений
cv2.imshow("Original Color", color_img)
cv2.imshow("Gray Image", gray_img)
cv2.imshow("Unchanged Image", unchanged_img)

# 0 = ждать бесконечно
# Нажать любую клвишу что бы закрыть все
cv2.waitKey(0)

# Закрытие всех окон
cv2.destroyAllWindows()
