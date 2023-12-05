import json

class YoloObject:
	def __init__(self, name: str, location: (float, float), confidence: float):
		self.name = name
		self.location = location
		self.confidence = confidence

def fromjson(jsonstr: str) -> list[YoloObject]:
	return [YoloObject(obj["name"], obj["location"], obj["confidence"]) for obj in json.loads(jsonstr)]