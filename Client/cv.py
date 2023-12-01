import detect
import threading

class Yolo:
	def __init__(self):
		self.__objects = []
		self.__condition = threading.Condition()

	def start(self, source):
		ready = threading.Condition()

		self.__thread = threading.Thread(target=self.__runyolo, args=(ready, source), daemon=True)
		self.__thread.start()

	def getobjects(self) -> list[(str, (float, float))]:
		with self.__condition:
			self.__condition.wait()

			return self.__objects

	def setobjects(self, objects: list[(str, (float, float))]):
		with self.__condition:
			self.__objects = objects

			self.__condition.notify_all()

	def __runyolo(self, ready: threading.Condition, source):
		detect.run(self, ready, source=source)