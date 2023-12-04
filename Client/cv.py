import detect
import threading

class YoloObject:
	def __init__(self, name: str, location: (float, float), confidence: float):
		self.name = name
		self.location = location
		self.confidence = confidence

class YoloResult:
	def __init__(self, objects: list[YoloObject] = [], frame: bytes = b""):
		self.objects = objects
		self.frame = frame

class Yolo:
	def __init__(self):
		self.__result = None
		self.__newresult = YoloResult()
		self.__condition = threading.Condition()
  
		self.__filter = ['cup', 'bottle', 'mouse']

	def start(self, source):
		ready = threading.Condition()
		self.__thread = threading.Thread(target=self.__runyolo, args=(ready, source), daemon=True)
		self.__thread.start()

		with ready:
			ready.wait()
   
	def set_filter(self, new_filter):
		self.__filter = new_filter
       
	def getresult(self) -> YoloResult:
		with self.__condition:
			self.__condition.wait()

			return self.__result

	def addobject(self, name: str, location: (float, float), confidence: float):
		self.__newresult.objects.append(YoloObject(name, location, confidence))

	def setframe(self, frame: bytes):
		self.__newresult.frame = frame

	def readyresult(self):
		with self.__condition:
			self.__result = self.__newresult
			self.__newresult = YoloResult()
			self.__condition.notify_all()

	def __runyolo(self, ready: threading.Condition, source):
		detect.run(self, self.__filter, ready, source=source)