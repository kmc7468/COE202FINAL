import threading
import detect

class Yolo:
    def __init__(self):
        thread = threading.Thread(target=func, daemon=True)
		thread.start()
    
    def start(self):
        self.thread.start()
    
    def getObject(self):
        return detect.objects[-1].objectName

	def getCoordinates(self):
    	return detect.objects[-1].coordinates

def func():
	detect.run(source=0)
thread = threading.Thread(target=func, daemon=True)
thread.start()

def get():
	return detect.objects[-1]

input()
print(get())


    
