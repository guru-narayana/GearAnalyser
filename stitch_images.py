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

def stitch_images_from_folder(folder):
    images = load_images_from_folder(folder)
    mode  = cv2.Stitcher_SCANS
    stittcher = cv2.Stitcher.create(mode)
    ret,pano = stittcher.stitch(images)
    return ret,pano

