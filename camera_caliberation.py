import cv2
from math import dist
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

class caliberate_device:
    def __init__(self) -> None:
        self.ids_order = np.array([0,1,2,3]) ### the order of IDS and corresponing heights
        self.heights = np.array([5,10,15,25]) ## heights at which ids are placed 
        self.curve_order  = 2
        self.original_dimension = 19

    def caliberate(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
        parameters =  cv2.aruco.DetectorParameters_create()
        corners, ids, rejectedCandidates = cv2.aruco.detectMarkers(gray,dictionary,parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        d = []
        if(len(ids)==0):
            print("ERROR No ids detected")
        for i in range(len(ids)):
            c = corners[i][0]
            d.append( self.original_dimension/((dist(c[0], c[1]) +  dist(c[1], c[2])+ dist(c[2], c[3])+ dist(c[3], c[1]))/4))
        p = np.polyfit(self.heights,d,self.curve_order)
        return p
    