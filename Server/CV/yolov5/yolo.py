import threading
import time
import logging
import detect

class Yolo:
    def __init__(self):
        self.thread = threading.Thread(target=self.func, daemon=True)
        self.condition = threading.Condition()
            
    def start(self):
        self.thread.start()
    
    def getObject(self):
        with self.condition:
            self.condition.wait()
            return detect.objects[-1]
                
    def setObject(self, object):
        with self.condition:
            detect.objects.append(object)
            self.condition.notify_all()
    
    def func(self):
        detect.run(source = 0, pipe = self)
 
yolo = Yolo()
yolo.thread.start()

def get():
	return detect.objects[-1]

input()
print(yolo.getObject())


    
