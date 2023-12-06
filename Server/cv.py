import json
import server
import threading

class Object:
	def __init__(self, name: str, location: (float, float), confidence: float):
		self.name = name
		self.location = location
		self.confidence = confidence

class Result:
	def __init__(self, objects: list[Object]):
		self.objects = objects

class Pipe:
	def __init__(self, srv: server.Connection):
		self.__srv = srv
		self.__result = None
		self.__resultcondition = threading.Condition()

	def getresult(self) -> Result:
		self.__srv.send("vision", None)

		with self.__resultcondition:
			self.__resultcondition.wait()

			return self.__result

	def setresult(self, result: Result):
		with self.__resultcondition:
			self.__result = result
			self.__resultcondition.notify_all()

def fromjson(jsonstr: str) -> Result:
	return Result([Object(obj["name"], obj["location"], obj["confidence"]) for obj in json.loads(jsonstr)])