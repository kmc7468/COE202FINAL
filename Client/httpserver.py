import http.server
import os
import threading

PORT = int(os.getenv("PORT"))

class RequestHandler(http.server.BaseHTTPRequestHandler):
	def __init__(self, server, *args):
		self.__server = server

		super().__init__(*args)

	def do_GET(self):
		if self.path == "/camera":
			self.send_response(200)

			self.send_header("Age", 0)
			self.send_header("Cache-Control", "no-cache, private")
			self.send_header("Pragma", "no-cache")
			self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
			self.end_headers()

			while True:
				frame = self.__server.getcameraframe()

				self.wfile.write(b"--FRAME\r\n")

				self.send_header("Content-Type", "image/jpeg")
				self.send_header("Content-Length", len(frame))
				self.end_headers()

				self.wfile.write(frame)
				self.wfile.write(b"\r\n")
		else:
			self.send_response(404)

class HTTPServer:
	def __init__(self, port: int = PORT):
		def reqhandler(*args):
			RequestHandler(self, *args)

		self.__server = http.server.HTTPServer(("localhost", port), reqhandler)
		self.__serverthread = None

		self.__cameraframe = None
		self.__cameraframecondition = threading.Condition()

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
			self.__cameraframecondition.wait_for(lambda: self.__cameraframe is not None)

			result = self.__cameraframe
			self.__cameraframe = None

			return result

	def setcameraframe(self, frame: bytes):
		with self.__cameraframecondition:
			self.__cameraframe = frame

			self.__cameraframecondition.notify()