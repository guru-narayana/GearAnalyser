import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images
images = load_images_from_folder("E:\Official_projects\Gear_analysis\src\data\Test_images\stitch_images1")
print(len(images))

mode  = cv2.Stitcher_SCANS

stittcher = cv2.Stitcher.create(mode)
ret,pano = stittcher.stitch(images)

if(ret == cv2.Stitcher_OK):

    filename = "E:\Official_projects\Gear_analysis\src\data\Test_images\Final.png"
    cv2.imwrite(filename,pano)   

