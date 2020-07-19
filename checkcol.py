import cv2
import numpy

img = cv2.imread("sample.jpg")

for i in range(0, 160):
    for j in range(0,320):
        print(tuple(img[i, j]))