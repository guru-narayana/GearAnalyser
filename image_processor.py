import cv2
from math import sqrt,dist
import matplotlib.pyplot as plt
from scipy.signal import argrelmax,argrelmin,savgol_filter,resample,correlate
from scipy.cluster.vq import kmeans, vq
import numpy as np
from camera_caliberation import caliberate_device

class image_processor:

    def __init__(self,using_CAD_Image = False) -> None:
        # Parameters
        self.__gear_cnt = [] # contour sorrouning the gear
        self.is_CAD_Image = using_CAD_Image
        self.gear_center = [0,0]
        self.outside_diameter = 0
        self.root_diameter = 0
        self.pitch_diameter = 0
        self.gear_count = 0
        self.gear_dists = np.array([]) # distance of each contour point from the conter
        self.gear_teeth_profiles = []
        self.gear_local_mins = []
        self.gear_teeth_errs = []
        self.pixel2mm = 0
        self.edge_thickness = 5
        self.dedundum_thickness_lst = []
        self.apendum_thickness_lst = []
        self.pitch_thickness_lst = []

        # ERROR FLAGS
        self.NO_GEAR_ERROR = False
        self.CENTER_CALCULATION_ERROR = False
        self.IMAGE_PROCESSED = False
        self.PIXEL2MM_UNSET = True

        # Tunable parameters
        self.adaptiveThresholdKernel = 901
        self.savgolWindowLength  = 7

    def set_frame(self,frame):
        self.frame = frame
        self.image_with_edges = frame*0 + 37
        self.image_with_errors = self.image_with_edges
   
    def get_teeth_metrices(self):
        for i in range(len(self.gear_teeth_profiles)):
            profile = self.gear_teeth_profiles[i]

            ## calculation for dedenum thickness
            indx1,indx2 = 0,0
            flag1,flag2 = True,True
            for j in range(len(profile)):
                if (profile[j]*2*self.pixel2mm > 1.05*self.root_diameter and flag1):
                    indx1 = j
                    flag1 = False
                if (profile[len(profile)-j-1]*2*self.pixel2mm > 1.05*self.root_diameter and flag2):
                    indx2 = len(profile)-j-1
                    flag2 = False
            pos1,pos2 = 0,0
            if(i == len(self.gear_teeth_profiles)-1):
                if(indx1+self.gear_local_mins[-1]<len(self.gear_dists)):
                    pos1 = self.__gear_cnt[indx1+self.gear_local_mins[-1]]
                else:
                    pos1 = self.__gear_cnt[indx1+self.gear_local_mins[-1]-len(self.gear_dists)]

                if(indx2+self.gear_local_mins[-1]<len(self.gear_dists)):
                    pos2 = self.__gear_cnt[indx2+self.gear_local_mins[-1]]
                else:
                    pos2 = self.__gear_cnt[indx2+self.gear_local_mins[-1]-len(self.gear_dists)]
            else:
                pos1 = self.__gear_cnt[self.gear_local_mins[i]+indx1]
                pos2 = self.__gear_cnt[self.gear_local_mins[i]+indx2]
            self.dedundum_thickness_lst.append(dist(pos1[0],pos2[0])*self.pixel2mm)

            ## calculation for apendum thickness
            indx1,indx2 = 0,0
            flag1,flag2 = True,True
            for j in range(len(profile)):
                if (profile[j]*2*self.pixel2mm > 0.99*self.outside_diameter and flag1):
                    indx1 = j
                    flag1 = False
                if (profile[len(profile)-j-1]*2*self.pixel2mm > 0.99*self.outside_diameter and flag2):
                    indx2 = len(profile)-j-1
                    flag2 = False
            pos1,pos2 = 0,0

            if(indx1 != 0 and indx2 != 0):
                if(i == len(self.gear_teeth_profiles)-1):
                    if(indx1+self.gear_local_mins[-1]<len(self.gear_dists)):
                        pos1 = self.__gear_cnt[indx1+self.gear_local_mins[-1]]
                    else:
                        pos1 = self.__gear_cnt[indx1+self.gear_local_mins[-1]-len(self.gear_dists)]

                    if(indx2+self.gear_local_mins[-1]<len(self.gear_dists)):
                        pos2 = self.__gear_cnt[indx2+self.gear_local_mins[-1]]
                    else:
                        pos2 = self.__gear_cnt[indx2+self.gear_local_mins[-1]-len(self.gear_dists)]
                else:
                    pos1 = self.__gear_cnt[self.gear_local_mins[i]+indx1]
                    pos2 = self.__gear_cnt[self.gear_local_mins[i]+indx2]
                    
                self.apendum_thickness_lst.append(dist(pos1[0],pos2[0])*self.pixel2mm)
            else:
                self.apendum_thickness_lst.append(0)

            ## calculation for pitch thickness
            indx1,indx2 = 0,0
            flag1,flag2 = True,True
            for j in range(len(profile)):
                if (profile[j]*2*self.pixel2mm > 0.99*self.pitch_diameter and flag1):
                    indx1 = j
                    flag1 = False
                if (profile[len(profile)-j-1]*2*self.pixel2mm > 0.99*self.pitch_diameter and flag2):
                    indx2 = len(profile)-j-1
                    flag2 = False
            pos1,pos2 = 0,0

            if(indx1 != 0 and indx2 != 0):
                if(i == len(self.gear_teeth_profiles)-1):
                    if(indx1+self.gear_local_mins[-1]<len(self.gear_dists)):
                        pos1 = self.__gear_cnt[indx1+self.gear_local_mins[-1]]
                    else:
                        pos1 = self.__gear_cnt[indx1+self.gear_local_mins[-1]-len(self.gear_dists)]

                    if(indx2+self.gear_local_mins[-1]<len(self.gear_dists)):
                        pos2 = self.__gear_cnt[indx2+self.gear_local_mins[-1]]
                    else:
                        pos2 = self.__gear_cnt[indx2+self.gear_local_mins[-1]-len(self.gear_dists)]
                else:
                    pos1 = self.__gear_cnt[self.gear_local_mins[i]+indx1]
                    pos2 = self.__gear_cnt[self.gear_local_mins[i]+indx2]
                    
                self.pitch_thickness_lst.append(dist(pos1[0],pos2[0])*self.pixel2mm)
            else:
                self.pitch_thickness_lst.append(0)
        
        print(self.apendum_thickness_lst)
        print(self.pitch_thickness_lst)
        print(self.dedundum_thickness_lst)

    def process(self,savgolWindowLength=None):
        self.NO_GEAR_ERROR = False
        self.CENTER_CALCULATION_ERROR = False
        self.IMAGE_PROCESSED = False
        self.PIXEL2MM_UNSET = True
        if len(self.frame.shape)==3:
            gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
        else:
            gray = self.frame
        Binary_image = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,self.adaptiveThresholdKernel,2)
        contours, _ = cv2.findContours(Binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if(len(contours) == 0):
            self.NO_GEAR_ERROR = True # check if no contours are present 
            return        
        self.__gear_cnt,max_area= contours[0],0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if(area>max_area and not (area >= gray.shape[1]*gray.shape[0]*0.9)): # getting the contour with maximum area
                self.__gear_cnt,max_area = cnt,area
        cv2.drawContours(self.image_with_edges, self.__gear_cnt, -1, (255, 255, 255), self.edge_thickness)
        M = cv2.moments(self.__gear_cnt)
        if M['m00'] != 0:
            self.gear_center[0] = int(M['m10']/M['m00'])
            self.gear_center[1] = int(M['m01']/M['m00'])
        else:
            self.CENTER_CALCULATION_ERROR = True # if centers are not found
        self.IMAGE_PROCESSED = True
        self.__find_gearProfiles(savgolWindowLength)

    def set_pixel2mm(self,k,calbrtn_param = []):
        if(len(calbrtn_param) == 0): # using diameter for pixel2mm constant calsulation
            self.pixel2mm = k/(self.outside_diameter)
        else: # using caliberation constants
            self.pixel2mm = 0
            for i in range(len(calbrtn_param)):
                self.pixel2mm += calbrtn_param[i]*k**(len(calbrtn_param)-1-i)
        self.outside_diameter = self.outside_diameter*self.pixel2mm
        self.root_diameter = self.pixel2mm*self.root_diameter
        self.PIXEL2MM_UNSET = False

    def compare_with_cad(self,gear_profile = None,threshold = 1):
        if(self.is_CAD_Image):
            print("Call compare from real gear image not cad")
            return
        elif(gear_profile.all() == None):
            print("Pass the profile from the cad")
            return
        elif(self.PIXEL2MM_UNSET):
            print("Set pixel to mm constant")
            return
        ac = max(correlate(self.__normalize(gear_profile),self.__normalize(gear_profile),"full","direct"))
        for profile in self.gear_teeth_profiles:
            profile*=self.pixel2mm
            if(len(profile)>len(gear_profile)):
                profile = resample(profile,len(gear_profile))
            cr = max(correlate(self.__normalize(profile),self.__normalize(gear_profile),"full","direct"))
            if(abs(cr-ac)/ac>threshold/100):
                self.gear_teeth_errs.append((abs(cr-ac)/ac))
            else:
                self.gear_teeth_errs.append(0)
        for i in range(len(self.gear_teeth_errs)-1):
            err =  self.gear_teeth_errs[i]
            if(err != 0):
                red = (0,0,min(err*200*100/threshold,255))
                cnt = self.__gear_cnt[self.gear_local_mins[i]:self.gear_local_mins[i+1]]
                cv2.drawContours(self.image_with_errors, cnt, -1, red, 3)
        if(self.gear_teeth_errs[-1]!=0):
            err =  self.gear_teeth_errs[-1]
            red = (0,0,min(err*200*100/threshold,255))
            cnt = np.concatenate((self.__gear_cnt[:self.gear_local_mins[0]],self.__gear_cnt[self.gear_local_mins[-1]:]))
            cv2.drawContours(self.image_with_errors, cnt, -1, red, self.edge_thickness+2)

    def __normalize(self,arr):
        norm_arr = []
        diff_arr = max(arr) - min(arr)   
        for i in arr:
            temp = ((i - min(arr))/diff_arr)
            norm_arr.append(temp)
        return norm_arr

    def __find_gearProfiles(self,savgolWindowLength = None):
        if(not self.IMAGE_PROCESSED):
            print("Process the image first to get the gear count")
            return
        gd = []
        for pnt in self.__gear_cnt:
            gd.append(sqrt((pnt[0][0] - self.gear_center[0])**2 + (pnt[0][1] - self.gear_center[1])**2)) ## generating the gear outer profile
        if(savgolWindowLength == None):
            self.savgolWindowLength = min(0.5*len(gd)/100,21)
        else:
            self.savgolWindowLength = savgolWindowLength
        self.gear_dists = np.array(savgol_filter(gd, window_length=self.savgolWindowLength, polyorder=1, mode="nearest")) ## filtering the outer profile
        seperator = self.__get_seperator() ## getting seperater between root and outer diameter


        minimas,temp1,ind,temp2 = [],[],[],[] ## getting minimas from the profile
        for i in range(len(self.gear_dists)):
            if self.gear_dists[i]<seperator:
                temp1.append(self.gear_dists[i])
                temp2.append(int(i))
            elif temp1!=[] and temp2!=[]:
                minimas.append(temp1)
                ind.append(temp2)
                temp1,temp2 = [],[]
        if(self.gear_dists[0]<seperator): ## satisfying the circular symmetry
            minimas[-1],ind[-1] = minimas[-1] + minimas[0],ind[-1]+ind[0]
            minimas,ind = minimas[1:],ind[1:]
        for i in range(len(minimas)):
            self.gear_local_mins.append(ind[i][np.argmin(minimas[i])])


        self.gear_count = len(self.gear_local_mins)
        if(self.is_CAD_Image):
            self.gear_teeth_profiles = self.gear_dists[self.gear_local_mins[0]:self.gear_local_mins[1]]
            return
        for i in range(len(self.gear_local_mins)-1): ### if the teeth profile is need to found for real image all teeth are used 
            self.gear_teeth_profiles.append(self.gear_dists[self.gear_local_mins[i]:self.gear_local_mins[i+1]])
        self.gear_teeth_profiles.append(np.concatenate((self.gear_dists[self.gear_local_mins[-1]:],self.gear_dists[:self.gear_local_mins[0]]))) ## circular symmetry

        ## plot for visualising the teethprofiles
        # for i in range(len(self.gear_teeth_profiles)-1):
        #     plt.scatter(range(self.gear_local_mins[i],self.gear_local_mins[i+1]),self.gear_teeth_profiles[i])
        # plt.scatter(list(range(self.gear_local_mins[-1],len(self.gear_dists)))+list(range(0,self.gear_local_mins[0])), self.gear_teeth_profiles[-1])
        # plt.show()

    def __get_seperator(self): ## generates a seperator value between maximum and minimum values, also finds root and outer diameter
        extremes =  np.concatenate((argrelmin(self.gear_dists)[0],argrelmax(self.gear_dists)[0]))
        centroids, mean_value = kmeans(self.gear_dists[extremes], 2)
        clusters, distances = vq(self.gear_dists[extremes], centroids)
        c1,c2 = [],[]
        for i in range(len(extremes)):
            if(clusters[i] == 0):
                c1.append(extremes[i])
            else:
                c2.append(extremes[i])
        if(centroids[0]>centroids[1]):
            minim = min(self.gear_dists[c1])
            maxim = max(self.gear_dists[c2])
            self.outside_diameter = centroids[0]*2
            self.root_diameter = centroids[1]*2
        else:
            minim = min(self.gear_dists[c2])
            maxim = max(self.gear_dists[c1])
            self.outside_diameter = centroids[1]*2
            self.root_diameter = centroids[0]*2
        seperator = (minim + maxim)/2
        # plt.figure(figsize=(20, 10), dpi=100)
        # plt.plot(self.gear_dists,color='green')
        # plt.scatter(c1,self.gear_dists[c1],color='red')
        # plt.scatter(c2,self.gear_dists[c2],color='blue')
        # plt.axhline(y = seperator, color = 'r', linestyle = '-')
        # plt.show()
        return seperator

            

if(__name__ == "__main__"):
    frame = cv2.imread("E:\Official_projects\Gear_analysis\src\data\Test_images\Test_single_gear\WIN_20230302_13_42_01_Pro.jpg")
    gear = image_processor()
    gear.set_frame(frame)
    gear.process()
    gear.set_pixel2mm(51)
    gear.get_teeth_metrices()
