import customtkinter
import PIL.Image
import PIL.ImageTk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import cv2
import numpy as np
import os
from camera_caliberation import caliberate_device
from image_processor import image_processor
from servo_control import servo
from stitch_images import stitch_images_from_folder

class Gear_analyser(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.title("Gear Analyser")
        self.iconbitmap("data/logo.ico")
        self.height = 720
        self.width = 1100
        self.geometry(str(self.width)+"x"+str(self.height))
        self.resizable(False, False)
        self.myservo = servo()
        


        self.insert_tools()
        self.caliberator  = caliberate_device()
        self.caliberation_params = None
        self.original_image_processed = False
        self.processor = image_processor()
        self.cad_processor = image_processor(using_CAD_Image=True)

        if(len(self.cameras)!=0):
            self.use_video()

    def insert_tools(self):
        self.update_status()
        self.myservo = servo()

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
        self.cad_frame = np.uint8( np.zeros((300,400,3)))
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        except:
            print("resolution not set")
        self.cameras = []

        self.update_cameras_available()

        ### chosseing camera
        update_btn = customtkinter.CTkButton(master=self, text="Update Ports", command=self.update_cameras_available,font=("Heebo", 14),width=120)
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
        self.processing_frame = customtkinter.CTkFrame(master=self, width=230, height=180+70+13)
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




        self.usingdiam_pitch_label = customtkinter.CTkLabel(master=self, text="Pitch Diameter : ",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 14))
        self.usingdiam_pitch_label.place(x=20, y=128+42)
        self.pitch_diam_height_mm_entry = customtkinter.CTkEntry(master=self, placeholder_text="value in mm",width=90)
        self.pitch_diam_height_mm_entry.place(x=130, y=128+42)


        self.savgol_switch_var = customtkinter.StringVar(value="off")
        self.savgol_switch_1 = customtkinter.CTkSwitch(master=self, text="Savgol window : ", command=self.savgol_wntry_switch_event,
                                   variable=self.savgol_switch_var, onvalue="on", offvalue="off")
        self.savgol_switch_1.place(x=10, y=167+42)

        self.savgol_entry = customtkinter.CTkEntry(master=self, placeholder_text="value",width=70)
        self.savgol_entry.place(x=160, y=167+42)
        self.savgol_entry.configure(state="disabled")

        self.adaptiveThresholdKernel_switch_var = customtkinter.StringVar(value="off")
        self.adaptiveThresholdKernel_switch_1 = customtkinter.CTkSwitch(master=self, text="adaptiveTKernel : ", command=self.adaptiveThresholdKernel_wntry_switch_event,
                                   variable=self.adaptiveThresholdKernel_switch_var, onvalue="on", offvalue="off")
        self.adaptiveThresholdKernel_switch_1.place(x=10, y=246)

        self.adaptiveThresholdKernel_entry = customtkinter.CTkEntry(master=self, placeholder_text="901",width=70)
        self.adaptiveThresholdKernel_entry.place(x=160, y=246)
        self.adaptiveThresholdKernel_entry.configure(state="disabled")
        

        self.process_image_btn = customtkinter.CTkButton(master=self, text="Process", command=self.process_image,font=("Heebo", 14),width=100)
        self.process_image_btn.place(x=15,y=206+66+10)

        self.caliberated = False
        self.caliberate_image_btn = customtkinter.CTkButton(master=self, text="Caliberate", command=self.caliberate,font=("Heebo", 14),width=100)
        self.caliberate_image_btn.place(x=125,y=206+66+10)

        ### compare

        self.cad_processing_frame = customtkinter.CTkFrame(master=self, width=230, height=205)
        self.cad_processing_frame.place(x=10,y=250+70+10)
        self.cad_process_label = customtkinter.CTkLabel(master=self, text="CAD",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 16))
        self.cad_process_label.place(x=85, y=255+70+10)
        self.cad_browse_btn = customtkinter.CTkButton(master=self, text="Browse CAD image", command=self.browse_cad_image,font=("Heebo", 12),width=120)
        self.cad_browse_btn.place(x=55,y=286+70+10)
        self.cad_usingdiam_label = customtkinter.CTkLabel(master=self, text="CAD Diameter : ",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 14))
        self.cad_usingdiam_label.place(x=20, y=328+10+70)

        self.cad_diam_mm_val = customtkinter.StringVar(value="0")
        self.cad_diam_mm_entry = customtkinter.CTkEntry(master=self, placeholder_text="value in mm",width=90)
        self.cad_diam_mm_entry.place(x=130, y=327+70+10)
        self.cad_diam_mm_entry.configure(state="disabled")

        self.usingerror_switch_var = customtkinter.StringVar(value="off")
        self.usingerror_switch_1 = customtkinter.CTkSwitch(master=self, text="Set Accept. Error : ", command=self.compare_error_switch_event,
                                   variable=self.usingerror_switch_var, onvalue="on", offvalue="off")
        self.usingerror_switch_1.place(x=10, y=371+70+10)

        self.cad_error_entry = customtkinter.CTkEntry(master=self, placeholder_text="% value",width=70)
        self.cad_error_entry.place(x=160, y=371+70+10)
        self.cad_error_entry.configure(state="disabled")

        self.cad_compare_btn = customtkinter.CTkButton(master=self, text="Compare", command=self.cad_compare,font=("Heebo", 14),width=120)
        self.cad_compare_btn.place(x=55,y=412+70+10)
        self.cad_compare_btn.configure(state="disabled")
        
        ## stitch images

        self.stitch_processing_frame = customtkinter.CTkFrame(master=self, width=230, height=168)
        self.stitch_processing_frame.place(x=10,y=545)

        self.stitch_process_label = customtkinter.CTkLabel(master=self, text="Stitch Images",width=60,height=25,fg_color=("white", "gray17"),font=("Heebo", 16))
        self.stitch_process_label.place(x=80, y=550)

        self.servo_combobox = customtkinter.CTkOptionMenu(master=self,values = self.myservo.ports_dsc,command=self.servo_optionmenue_cb,font=("Heebo", 14),width=210,dynamic_resizing=False)
        self.servo_combobox.place(x = 19,y =585)
        self.servo_combobox.set(self.myservo.ports_dsc[-1])

        self.stitch_save_btn = customtkinter.CTkButton(master=self, text="Save Images", command=self.stitch_save_images,font=("Heebo", 14),width=120)
        self.stitch_save_btn.place(x=55,y=624)
        self.stitch_save_btn.configure(state="disabled")

        self.stitch_images_btn = customtkinter.CTkButton(master=self, text="Stitch Images", command=self.stitch_images,font=("Heebo", 14),width=120)
        self.stitch_images_btn.place(x=55,y=660)



        ## table control
        self.generate_table1()

    def generate_table1(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#494949",
                        fieldbackground="#494949",
                        rowheight=25,
                        foreground="white"
                        )
        style.map('Treeview',background="white")

        treev = ttk.Treeview(self, selectmode ='browse',height=9) 
        treev.place(x=260,y = 420+35)
        treev.configure(style="Treeview")
        
        treev["columns"] = ("1", "2", "3","4","5")
        treev['show'] = 'headings'

        label1 = Label(self, text="Teeth S.N.", bg='#494949',borderwidth=1, relief="ridge",fg= "white",font=("Arial", 8))
        label1.place(x=261,y=408+35,height=34,width=80)
        
        label2 = Label(self, text="Dedundum\n Thickness", bg='#494949',borderwidth=1, relief="ridge",fg= "white",font=("Arial", 8))
        label2.place(x=261+80,y=408+35,height=34,width=80)
        
        label3 = Label(self, text="Tooth\n Thickness", bg='#494949',borderwidth=1, relief="ridge",fg= "white",font=("Arial", 8))
        label3.place(x=261+160,y=408+35,height=34,width=80)
        
        label3 = Label(self, text="Addendum\n Thickness", bg='#494949',borderwidth=1, relief="ridge",fg= "white",font=("Arial", 8))
        label3.place(x=261+240,y=408+35,height=34,width=80)
        
        label3 = Label(self, text="Error\n with CAD", bg='#494949',borderwidth=1, relief="ridge",fg= "white",font=("Arial", 8))
        label3.place(x=261+320,y=408+35,height=34,width=82)

        treev.column("1", width = 80, anchor ='c')
        treev.column("2", width = 80, anchor ='c')
        treev.column("3", width = 80, anchor ='c')
        treev.column("4", width = 80, anchor ='c')
        treev.column("5", width = 80, anchor ='c')
        
        # treev.heading("1", text ="Teeth S.N.")
        # treev.heading("2", text ="Dedundum Thickness")
        # treev.heading("3", text ="Tooth Thickness")
        # treev.heading("4", text ="Addendum Thickness")
        # treev.heading("5", text ="Error")

        # treev.insert("", 'end',values =("Nidhi", "F", "25","5"))
        # treev.insert("", 'end',values =("Nidhi", "F", "25","5"))
        # treev.insert("", 'end',values =("Nidhi", "F", "25","5"))
        # treev.insert("", 'end',values =("Nidhi", "F", "25","5"))
        # treev.insert("", 'end',values =("Nidhi", "F", "25","5"))

    def stitch_images(self):
        self.update_status(1)
        self.update()
        source_path = filedialog.askdirectory(title='Select the Parent Directory')
        ret,image = stitch_images_from_folder(source_path)
        if(not ret):
            self.using_camera =0
            self.frame = image
            self.using_camera = 0
            self.original_image_processed = FALSE
        else:
            self.update_status(3,"Stitch Failed !!")
            return
        self.update_status()

    def stitch_save_images(self):
        self.update_status(1)
        source_path = filedialog.askdirectory(title='Select the Parent Directory')
        path = os.path.join(source_path, 'StitchImages')
        os.makedirs(path)
        for i in range(25):
            abs_path = path + "\Image" + str(i) + ".jpg"
            cv2.imwrite(abs_path,self.frame)
            imgtk = self.convert_image(self.frame)
            self.original_image.imgtk = imgtk
            self.original_image.configure(image=imgtk)
            self.update()
            self.update_live()
            self.myservo.turn_20()
        self.update_status()
        
    def servo_optionmenue_cb(self,choice):
        self.update_status(1)
        self.update()
        self.myservo.select_port(self.myservo.ports_dsc.index(choice))
        self.stitch_save_btn.configure(state="normal")
        self.update_status()

    def adaptiveThresholdKernel_wntry_switch_event(self):
        if(self.adaptiveThresholdKernel_switch_var.get()=="on"):
            self.adaptiveThresholdKernel_entry.configure(state="normal")
        else:
            self.adaptiveThresholdKernel_entry.configure(state="disabled")

    def savgol_wntry_switch_event(self):
        if(self.savgol_switch_var.get()=="on"):
            self.savgol_entry.configure(state="normal")
        else:
            self.savgol_entry.configure(state="disabled")

    def compare_error_switch_event(self):
        if(self.usingerror_switch_var.get()=="on"):
            self.cad_error_entry.configure(state="normal")
        else:
            self.cad_error_entry.configure(state="disabled")

    def browse_cad_image(self):
        filename = filedialog.askopenfilename(initialdir = "/",
                                        title = "Select a File",
                                        filetypes = (("jpg","*.jpg*"),("png","*.png*")))
        if(filename==""):
            return
        self.cad_frame = cv2.imread(filename)
        self.cad_compare_btn.configure(state="normal")
        self.cad_diam_mm_entry.configure(state="normal")

    def cad_compare(self):
        self.update_status(1)
        if(not self.original_image_processed):
            self.update_status(3,"Process Image")
            return
        self.cad_processor.set_frame(self.cad_frame)

        if(self.adaptiveThresholdKernel_switch_var.get()=="on"):
            self.cad_processor.adaptiveThresholdKernel  = int(self.adaptiveThresholdKernel_entry.get())
        else:
            self.cad_processor.adaptiveThresholdKernel = 901
        
        if(self.savgol_switch_var.get()=="on"):
            self.cad_processor.process(float(self.savgol_entry.get()))
        else:
            self.cad_processor.process()
        self.cad_processor.set_pixel2mm(float(self.cad_diam_mm_entry.get()))

        if(self.cad_diam_mm_entry.get()==""):
            self.update_status(3,"Enter Diameter")
            return
        
        if(self.usingerror_switch_var.get()=="on"):
            self.cad_compare_threshold = float(self.cad_error_entry.get())
        else:
            self.cad_compare_threshold = 5
        self.processor.compare_with_cad(self.cad_processor.gear_teeth_profiles, self.cad_compare_threshold)
        self.processed_frame =  self.processor.image_with_errors
        self.update_status()
        self.cad_compare_btn.configure(state="disabled")
        self.cad_diam_mm_entry.configure(state="disabled")
        self.cad_processor = image_processor(using_CAD_Image=True)
        self.original_image_processed  = False

    def caliberate(self):
        ret,self.caliberation_params =  self.caliberator.caliberate(frame=self.frame)
        if(not ret):
            self.update_status(3,"Caliberation Fail")
            self.caliberated = False
            return
        self.update_status()
        self.caliberated = True
        self.using_camera = 0

    def process_image(self):
        self.processor = image_processor()
        if(not self.caliberated and self.using_height_switch_var.get()=="on"):
            self.update_status(3,"Caliberate !!")
            return
        self.update_status(1)
        self.update()
        self.processor.set_frame(self.frame)


        if(self.adaptiveThresholdKernel_switch_var.get()=="on"):
            self.processor.adaptiveThresholdKernel  = int(self.adaptiveThresholdKernel_entry.get())
        else:
            self.processor.adaptiveThresholdKernel = 901
            

        if(self.savgol_switch_var.get()=="on"):
            self.processor.process(float(self.savgol_entry.get()))
        else:
            self.processor.process()

        if( self.processor.NO_GEAR_ERROR):
            self.update_status(3,"No Gear Detected")
        if(self.processor.CENTER_CALCULATION_ERROR):
            self.update_status(3,"Error in center")

        if(self.diam_height_mm_entry.get() == ""):
            self.update_status(3,"Enter value")
            return
        elif(self.using_height_switch_var.get()=="on"):
            self.processor.set_pixel2mm(float(self.diam_height_mm_entry.get()),self.caliberation_params)
        else:
            self.processor.set_pixel2mm(float(self.diam_height_mm_entry.get()))
        

        if(self.pitch_diam_height_mm_entry.get() == ""):
            self.processor.pitch_diameter = 0
        else:
            self.processor.pitch_diameter = float(self.pitch_diam_height_mm_entry.get())

        
        self.processed_frame = self.processor.image_with_edges
        self.original_image_processed = True
        self.using_camera = 0
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
        self.original_image_processed = False

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
        self.update_status(1)
        index = 0
        arr = []
        self.cap.release()
        self.myservo.get_ports()
        try:
            self.servo_combobox.configure(values = self.myservo.ports_dsc)
        except:
            pass
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
        self.update_status(0)

    def update_live(self):
        self.frame = self.cap.read()[1]
        self.original_image_processed = False

    def convert_image(self,image):
        cv2image= cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),(400,300))
        img = PIL.Image.fromarray(cv2image)
        imgtk = PIL.ImageTk.PhotoImage(image = img)
        return imgtk
    
    def update_status(self,status=0,txt=""):
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
        elif(status==3):
            self.status_label = customtkinter.CTkLabel(master=self, text=txt,width=60,height=25,fg_color=("white", "gray17"),text_color=("red"),font=("Heebo", 19))
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




