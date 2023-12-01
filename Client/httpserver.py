import http.server
import socketserver
import threading
import typing

class RequestHandler(http.server.SimpleHTTPRequestHandler):
	def __init__(self, server, *args):
		self.__server = server

		super().__init__(*args)

	def do_GET(self):
		if self.path == "/camera":
			self.__startstream(self.__server.getcameraframe)
		elif self.path == "/yolo":
			self.__startstream(self.__server.getyoloframe)
		else:
			self.send_error(404, "Page not found")

	def __startstream(self, getframe: typing.Callable[[], bytes]):
		self.send_response(200)

		self.send_header("Age", 0)
		self.send_header("Cache-Control", "no-cache, private")
		self.send_header("Pragma", "no-cache")
		self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
		self.end_headers()

		while True:
			frame = getframe()

			try:
				self.wfile.write(b"--FRAME\r\n")

				self.send_header("Content-Type", "image/jpeg")
				self.send_header("Content-Length", len(frame))
				self.end_headers()

				self.wfile.write(frame)
				self.wfile.write(b"\r\n")
			except:
				break

class DaemonThreadingTCPServer(socketserver.ThreadingTCPServer):
	daemon_threads = True

class HTTPServer:
	def __init__(self, port: int):
		def reqhandler(*args):
			RequestHandler(self, *args)

		self.__server = DaemonThreadingTCPServer(("localhost", port), reqhandler)
		self.__serverthread = None

		self.__cameraframe = None
		self.__cameraframecondition = threading.Condition()

		self.__yoloframe = None
		self.__yoloframecondition = threading.Condition()

	def __del__(self):
		self.stop()
		self.__server.server_close()

	def start(self):
		self.__serverthread = threading.Thread(target=self.__server.serve_forever, daemon=True)
		self.__serverthread.start()

	def stop(self):
		if self.__serverthread is not None:
			self.__server.shutdown()

			self.__serverthread.join()
			self.__serverthread = None

	def getcameraframe(self) -> bytes:
		with self.__cameraframecondition:
			self.__cameraframecondition.wait()

			return self.__cameraframe

	def setcameraframe(self, frame: bytes):
		with self.__cameraframecondition:
			self.__cameraframe = frame

			self.__cameraframecondition.notify_all()

	def getyoloframe(self) -> bytes:
		with self.__yoloframecondition:
			self.__yoloframecondition.wait()

			return self.__yoloframe

	def setyoloframe(self, frame: bytes):
		with self.__yoloframecondition:
			self.__yoloframe = frame

			self.__yoloframecondition.notify_all()