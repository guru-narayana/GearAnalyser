import numpy as np
import cv2
import random
  
img = cv2.imread("E:\Official_projects\Gear_analysis\src\data\Test_images\clock-face.png")

for i in range(150):
    int1 = random.randint(100, 1500)
    int2 = random.randint(100, 1500)
    cv2.rectangle(img, (int1, int2), (int1+i*3, int2+i*2), (0, 0, 0), 3)
    int1 = random.randint(100, 1500)
    int2 = random.randint(100, 1500)
    cv2.circle(img, (int1,int2), random.randint(1, 50), (0, 0, 0), 3)
    int1 = random.randint(100, 1500)
    int2 = random.randint(100, 1500)
    cv2.circle(img, (int1,int2), random.randint(1, 50), (100, 100, 100), -1)

filename = "E:\Official_projects\Gear_analysis\src\data\Test_images\clock-face2.png"
cv2.imwrite(filename, img)

stretch_near = cv2.resize(img, (780, 780),
               interpolation = cv2.INTER_LINEAR)

#cv2.imshow('dark', stretch_near)
#Allows us to see image
#until closed forcefully

cv2.waitKey(0)
cv2.destroyAllWindows()