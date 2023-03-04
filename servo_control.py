import serial.tools.list_ports
import time



class servo():
        def __init__(self) -> None:
                self.ports = []
                self.ports_dsc = []
                self.nano = None

        
        def get_ports(self,pnt = False):
                ports = serial.tools.list_ports.comports()

                for port, desc, hwid in sorted(ports):
                        self.ports.append(port)
                        self.ports_dsc.append(desc)
                        if(pnt):
                                print(port)

        def select_port(self,index):
                self.nano = serial.Serial('COM9', 9600, timeout=1)
                time.sleep(4)                
        def turn_30(self):
                if(self.nano == None):
                        print("select the port")
                        return
                self.nano.write(str.encode('30'))
                time.sleep(1)




if __name__=="__main__":
        s = servo()
        s.get_ports()
        s.select_port(4)
        s.turn_30()