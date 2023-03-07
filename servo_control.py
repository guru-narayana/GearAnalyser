import serial.tools.list_ports
import time



class servo():
        def __init__(self) -> None:
                self.ports = []
                self.ports_dsc = []
                self.nano = None

        
        def get_ports(self,pnt = False):
                ports = serial.tools.list_ports.comports()
                self.ports = []
                self.ports_dsc = []
                for port, desc, hwid in sorted(ports):
                        self.ports.append(port)
                        self.ports_dsc.append(desc)
                        if(pnt):
                                print(port)

        def select_port(self,index):
                if(type(self.nano) != type(None)):
                        self.nano.close()
                self.nano = serial.Serial(self.ports[index], 9600, timeout=1)
                time.sleep(4)                
        def turn_20(self):
                if(self.nano == None):
                        print("select the port")
                        return
                self.nano.write(str.encode('20'))
                time.sleep(2)




if __name__=="__main__":
        s = servo()
        s.get_ports()
        s.select_port(4)
        while(True):
                x = input()
                if(x=="1"):
                        s.turn_20()