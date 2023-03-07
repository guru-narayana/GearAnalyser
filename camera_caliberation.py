import cv2
from math import dist
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

class caliberate_device:
    def __init__(self) -> None:
        self.heights = np.array([5,10,15,25]) ## heights at which ids are placed 
        self.curve_order  = None
        self.original_dimension = 19

    def caliberate(self,frame):
        sucess = 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
        parameters =  cv2.aruco.DetectorParameters_create()
        corners, ids, rejectedCandidates = cv2.aruco.detectMarkers(gray,dictionary,parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        d = []
        if(type(ids)==type(None)):
            sucess = 0
            return sucess,ids
        for i in range(len(ids)):
            c = corners[i][0]
            d.append( self.original_dimension/((dist(c[0], c[1]) +  dist(c[1], c[2])+ dist(c[2], c[3])+ dist(c[3], c[1]))/4))
        h = self.heights[ids.transpose()[0]]
        if(self.curve_order == None):
            self.curve_order = len(h)-1
        p = np.polyfit(h,d,self.curve_order)
        return sucess,p
    
