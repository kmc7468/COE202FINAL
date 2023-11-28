import io
import os
import picamera
import threading

CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT"))
CAMERA_FPS = int(os.getenv("CAMERA_FPS"))

class CameraOutput:
	def __init__(self):
		self.__frame = None
		self.__buffer = io.BytesIO()
		self.__condition = threading.Condition()

	def getframe(self) -> bytes:
		with self.__condition:
			self.__condition.wait()

			return self.__frame

	def write(self, buffer: bytes) -> int:
		with self.__condition:
			if buffer.startswith(b"\xff\xd8"):
				self.__buffer.truncate()
				self.__frame = self.__buffer.getvalue()
				self.__buffer.seek(0)

				self.__condition.notify_all()

		return self.__buffer.write(buffer)

class Camera:
	def __init__(self):
		self.__camera = picamera.PiCamera()
		self.__output = CameraOutput()

	def getoutput(self) -> CameraOutput:
		return self.__output

	def start(self, resolution: tuple[int, int] = (CAMERA_WIDTH, CAMERA_HEIGHT), framerate: int = CAMERA_FPS):
		self.__camera.resolution = resolution
		self.__camera.framerate = framerate

		self.__camera.start_recording(self.__output, format="mjpeg")

	def stop(self):
		self.__camera.stop_recording()