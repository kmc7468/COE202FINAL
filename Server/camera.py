import io
import picamera
import threading

class CameraOutput:
	def __init__(self):
		self.__frame = None
		self.__buffer = io.BytesIO()
		self.__condition = threading.Condition()

	def getframe(self) -> bytes:
		with self.__condition:
			self.__condition.wait_for(lambda: self.__frame is not None)

			result = self.__frame
			self.__frame = None

			return result

	def write(self, buffer: bytes) -> int:
		with self.__condition:
			if buffer.startswith(b"\xff\xd8"):
				self.__buffer.truncate()
				self.__frame = self.__buffer.getvalue()
				self.__buffer.seek(0)

				self.__condition.notify()

		return self.__buffer.write(buffer)

class Camera:
	def __init__(self):
		self.__camera = picamera.PiCamera()
		self.__output = CameraOutput()

	def getoutput(self) -> CameraOutput:
		return self.__output

	def start(self, resolution: tuple[int, int] = (640, 480), framerate: int = 15):
		self.__camera.resolution = resolution
		self.__camera.framerate = framerate

		self.__camera.start_recording(self.__output, format="mjpeg")

	def stop(self):
		self.__camera.stop_recording()