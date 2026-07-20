"""
03. Поиск по цвету и поиск контуров
-------------------------------------
Часть А: ColorFinder — поиск объекта заданного цвета через веб-камеру
         (с трекбарами для подбора значений HSV в реальном времени).
Часть Б: findContours — поиск контуров фигур на статичном изображении.

Часть А требует камеру, часть Б — нет. Запустите нужную функцию в конце файла.
"""

import cv2
import cvzone
import numpy as np


def run_color_finder():
    """Поиск цвета через камеру с ползунками для подбора HSV."""
    myColorFinder = cvzone.ColorFinder(trackBar=True)
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    # Стартовые значения для оранжевого цвета — их можно двигать ползунками
    hsvVals = {'hmin': 10, 'smin': 55, 'vmin': 215,
               'hmax': 42, 'smax': 255, 'vmax': 255}

    while True:
        success, img = cap.read()
        if not success:
            break

        imgColor, mask = myColorFinder.update(img, hsvVals)
        imgStack = cvzone.stackImages([img, imgColor, mask], cols=3, scale=1)

        cv2.imshow("Поиск цвета", imgStack)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def run_find_contours():
    """Поиск контуров фигур на изображении, скачанном из интернета."""
    imgShapes = cvzone.downloadImageFromUrl(
        url='https://github.com/cvzone/cvzone/blob/master/Results/shapes.png?raw=true'
    )

    imgCanny = cv2.Canny(imgShapes, 50, 150)
    imgDilated = cv2.dilate(imgCanny, np.ones((5, 5), np.uint8), iterations=1)

    # Все контуры
    imgContours, conFound = cvzone.findContours(
        imgShapes, imgDilated, minArea=1000, sort=True,
        filter=None, drawCon=True, c=(255, 0, 0), ct=(255, 0, 255),
        retrType=cv2.RETR_EXTERNAL, approxType=cv2.CHAIN_APPROX_NONE
    )

    # Только треугольники и четырёхугольники
    imgContoursFiltered, conFoundFiltered = cvzone.findContours(
        imgShapes, imgDilated, minArea=1000, sort=True,
        filter=[3, 4], drawCon=True, c=(255, 0, 0), ct=(255, 0, 255),
        retrType=cv2.RETR_EXTERNAL, approxType=cv2.CHAIN_APPROX_NONE
    )

    cv2.imshow("Все контуры", imgContours)
    cv2.imshow("Только 3-4 угла", imgContoursFiltered)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Раскомментируйте нужную функцию для запуска
    run_find_contours()
    # run_color_finder()
