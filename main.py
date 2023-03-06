import customtkinter
import PIL.Image
import PIL.ImageTk
from tkinter import *
from tkinter import filedialog
import cv2
import numpy as np
import os
from camera_caliberation import caliberate_device
from image_processor import image_processor


class Gear_analyser(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gear Analyser")
        self.iconbitmap("data/logo.ico")
        self.height = 720
        self.width = 1100
        self.geometry(str(self.width)+"x"+str(self.height))
        self.resizable(False, False)


        self.insert_tools()
        self.caliberator  = caliberate_device()
        self.processor = image_processor()
        self.cad_processor = image_processor(using_CAD_Image=True)

        if(len(self.cameras)!=0):
            self.use_video()

    def insert_tools(self):
        self.update_status()

        ### setting up iamges and frames
        self.image_frame = customtkinter.CTkFrame(master=self, width=840, height=400)
        self.image_frame.place(x=250,y=10)
        self.original_image =Label(self,width=400,height=300)
        self.original_image.place(x=260,y=90)
        self.processed_image =Label(self,width=400,height=300)
        self.processed_image.place(x=680,y=90)
        img = PIL.Image.fromarray( np.zeros((300,400,3), np.uint8))
        imgtk = PIL.ImageTk.PhotoImage(image = img)
        self.original_image.imgtk = imgtk
        self.original_image.configure(image=imgtk)
        self.processed_image.imgtk = imgtk
        self.processed_image.configure(image=imgtk)

        original_label = customtkinter.CTkLabel(master=self, text="Original Image",width=120,height=25,fg_color=("white", "gray17"),font=("Heebo", 19))
        original_label.place(x=400, y=60)

        processed_label = customtkinter.CTkLabel(master=self, text="Processed Image",width=120,height=25,fg_color=("white", "gray17"),font=("Heebo", 19))
        processed_label.place(x=800, y=60)

        self.camera_index = 0
        self.using_camera = 1
        self.frame =  np.uint8(np.zeros((300,400,3)))
        self.processed_frame =np.uint8( np.zeros((300,400,3)))
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        except:
            print("resolution not set")
        self.cameras = []

        self.update_cameras_available()

        ### chosseing camera
        update_btn = customtkinter.CTkButton(master=self, text="Update cameras", command=self.update_cameras_available,font=("Heebo", 14),width=120)
        update_btn.place(x=270,y=20)

        ## image manipulation
        browse_btn = customtkinter.CTkButton(master=self, text="Browse Image", command=self.browse_image,font=("Heebo", 14),width=120)
        browse_btn.place(x=680,y=20)

        so_btn = customtkinter.CTkButton(master=self, text="Save original", command=self.save_original,font=("Heebo", 14),width=120)
        so_btn.place(x=820,y=20)

        sp_btn = customtkinter.CTkButton(master=self, text="Save processed", command=self.save_processed,font=("Heebo", 14),width=120)
        sp_btn.place(x=960,y=20)


        ## processing
        self.using_height_switch_var = customtkinter.StringVar(value="off")
        self.processing_frame = customtkinter.CTkFrame(master=self, width=230, height=150)
        self.processing_frame.place(x=10,y=60)
        self.process_label = customtkinter.CTkLabel(master=self, text="Process Image",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 16))
        self.process_label.place(x=70, y=60)
        self.usingheight_switch_1 = customtkinter.CTkSwitch(master=self, text="Use Height", command=self.height_switch_event,
                                   variable=self.using_height_switch_var, onvalue="on", offvalue="off")
        
        self.usingheight_switch_1.place(x=56, y=95)

        self.usingdiam_height_label = customtkinter.CTkLabel(master=self, text="Gear Diameter : ",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 14))
        self.usingdiam_height_label.place(x=20, y=128)

        self.diam_height_mm_val = customtkinter.StringVar(value="0")

        self.diam_height_mm_entry = customtkinter.CTkEntry(master=self, placeholder_text="value in mm",width=90)
        self.diam_height_mm_entry.place(x=130, y=128)

        self.process_image_btn = customtkinter.CTkButton(master=self, text="Process", command=self.process_image,font=("Heebo", 14),width=120)
        self.process_image_btn.place(x=50,y=170)


    def process_image(self):
        self.update_status(1)

        self.processor.set_frame(self.frame)
        self.processor.process()
        self.processed_frame = self.processor.image_with_edges
        if( self.processor.NO_GEAR_ERROR and  self.processor.CENTER_CALCULATION_ERROR and  self.processor.IMAGE_PROCESSED):
            self.update_status(2)

        self.update_status(0)
        
    def height_switch_event(self):
        self.usingdiam_height_label.destroy()
        if(self.using_height_switch_var.get() == "on"):
            self.usingdiam_height_label = customtkinter.CTkLabel(master=self, text="Gear Height : ",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 14))
            self.usingdiam_height_label.place(x=20, y=128)
        else:
            self.usingdiam_height_label = customtkinter.CTkLabel(master=self, text="Gear Diameter : ",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 14))
            self.usingdiam_height_label.place(x=20, y=128)
             
    def browse_image(self):
        filename = filedialog.askopenfilename(initialdir = "/",
                                        title = "Select a File",
                                        filetypes = (("jpg","*.jpg*"),("png","*.png*")))
        if(filename==""):
            return
        self.frame = cv2.imread(filename)
        self.using_camera = 0

    def save_original(self):        
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*") ))
        if(not filename):
            return
        abs_path = os.path.abspath(filename.name)
        cv2.imwrite(abs_path,self.frame)

    def save_processed(self):
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*") ))
        if(not filename):
            return
        abs_path = os.path.abspath(filename.name)
        cv2.imwrite(abs_path,self.processed_frame)

    def optionmenu_callback(self,choice):
        self.camera_index = int(choice[-1])

    def use_video(self):
        self.cap.release()
        self.cap = cv2.VideoCapture(self.camera_index,cv2.CAP_DSHOW)
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        except:
            print("resolution not set")
        self.using_camera = 1

    def update_cameras_available(self):
        index = 0
        arr = []
        self.cap.release()
        while True:
            cap = cv2.VideoCapture(index,cv2.CAP_DSHOW)
            if not cap.read()[0]:
                break
            else:
                arr.append("Camera " + str(index))
            cap.release()
            index += 1
        self.cameras = arr
        if(len(arr)!=0):
            self.camera_combobox = customtkinter.CTkOptionMenu(master=self,values = self.cameras,command=self.optionmenu_callback,font=("Heebo", 14),width=110)
            self.camera_combobox.place(x = 410,y =20)
            self.camera_combobox.set("Camera 0")
            self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
            except:
                print("resolution not set")
            use_video_btn = customtkinter.CTkButton(master=self, text="Use video", command=self.use_video,font=("Heebo", 14),width=120)
            use_video_btn.place(x=540,y=20)

    def update_live(self):
        self.frame = self.cap.read()[1]     

    def convert_image(self,image):
        cv2image= cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),(400,300))
        img = PIL.Image.fromarray(cv2image)
        imgtk = PIL.ImageTk.PhotoImage(image = img)
        return imgtk
    
    def update_status(self,status=0):
        self.status_frame = customtkinter.CTkFrame(master=self, width=230, height=40)
        self.status_frame.place(x=10,y=10)
        self.status1_label = customtkinter.CTkLabel(master=self, text="Status : ",width=60,height=25,fg_color=("white", "gray17"),font=("Lao UI", 15))
        self.status1_label.place(x=20, y=20)
        
        if(status == 0):
            self.status_label = customtkinter.CTkLabel(master=self, text="Free",width=60,height=25,fg_color=("white", "gray17"),text_color=("green"),font=("Heebo", 19))
            self.status_label.place(x=80, y=20)
        elif(status==1):
            self.status_label = customtkinter.CTkLabel(master=self, text="Processing ...",width=60,height=25,fg_color=("white", "gray17"),text_color=("blue"),font=("Heebo", 19))
            self.status_label.place(x=80, y=20)
        elif(status==2):
            self.status_label = customtkinter.CTkLabel(master=self, text="Failed !!",width=60,height=25,fg_color=("white", "gray17"),text_color=("red"),font=("Heebo", 19))
            self.status_label.place(x=80, y=20)

    def loop(self):
        if(self.using_camera):
            self.update_live()
        imgtk = self.convert_image(self.frame)
        self.original_image.imgtk = imgtk
        self.original_image.configure(image=imgtk)

        imgtk = self.convert_image(self.processed_frame)
        self.processed_image.imgtk = imgtk
        self.processed_image.configure(image=imgtk)


        self.after(30, self.loop)


app = Gear_analyser()
app.loop()
app.mainloop()




