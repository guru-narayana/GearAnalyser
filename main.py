import customtkinter


class Gear_analyser(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gear Analyser")
        self.iconbitmap("data/logo.ico")
        self.height = 800
        self.width = 1000
        x = (self.winfo_screenwidth()//2) - (self.width//2)
        y = (self.winfo_screenheight()//2) - (self.height//2)
        self.geometry('{}x{}+{}+{}'.format(self.width,self.height,x,y))

        self.insert_tools()
    def insert_tools(self):
        pass



app = Gear_analyser()
app.mainloop()




