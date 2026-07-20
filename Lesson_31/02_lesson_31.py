"""
02. Инструменты для работы с изображениями
--------------------------------------------
  - downloadImageFromUrl — скачать картинку по ссылке (в т.ч. с прозрачностью)
  - overlayPNG           — наложить PNG с альфа-каналом поверх кадра
  - rotateImage          — повернуть изображение
  - stackImages          — склеить несколько кадров в один для показа

Эта часть НЕ требует камеры — можно запускать на любом компьютере.
"""

import cv2
import cvzone
from cvzone.Utils import rotateImage

# 1. Загрузка изображений по URL ---
imgNormal = cvzone.downloadImageFromUrl(
    url='https://github.com/cvzone/cvzone/blob/master/Results/shapes.png?raw=true'
)

imgPNG = cvzone.downloadImageFromUrl(
    url='https://github.com/cvzone/cvzone/blob/master/Results/cvzoneLogo.png?raw=true',
    keepTransparency=True
)
imgPNG = cv2.resize(imgPNG, (0, 0), None, 1.5, 1.5)

cv2.imshow("Обычное изображение", imgNormal)

# 2. Наложение PNG с прозрачностью на другое изображение ---
imgBase = imgNormal.copy()
imgOverlay = cvzone.overlayPNG(imgBase, imgPNG, pos=[20, 20])
cv2.imshow("PNG наложен поверх", imgOverlay)

# 3. Поворот изображения ---
imgRotated = rotateImage(imgNormal, 60, scale=1, keepSize=False)
imgRotatedKeepSize = rotateImage(imgNormal, 60, scale=1, keepSize=True)

# 4. Склейка нескольких изображений в сетку ---
imgGray = cv2.cvtColor(imgNormal, cv2.COLOR_BGR2GRAY)
imgCanny = cv2.Canny(imgGray, 50, 150)

imgList = [imgNormal, imgGray, imgCanny, imgRotated]
stackedImg = cvzone.stackImages(imgList, cols=2, scale=0.7)

cv2.imshow("Склейка изображений", stackedImg)

print("Нажмите любую клавишу в окне изображения, чтобы закрыть все окна")
cv2.waitKey(0)
cv2.destroyAllWindows()
