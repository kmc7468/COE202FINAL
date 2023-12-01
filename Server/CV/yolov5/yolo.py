import threading
import detect

class Yolo:
    def __init__(self):
        self.thread = threading.Thread(target=self.func, daemon=True)
        self.condition = threading.Condition()
            
    def start(self):
        self.thread.start()
    
    def getObject(self):
        return detect.objects[-1].objectName
    
    def getCoordinates(self):
        return detect.objects[-1].coordinates
    
    def func(self):
        detect.run(source = 0)
 
yolo = Yolo()
yolo.thread.start()

def get():
	return detect.objects[-1]

input()
# print(get())
print(yolo.getObject(), yolo.getCoordinates())


    
