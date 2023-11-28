import os
import sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

import server

srv = server.Connection()

addr = "localhost"
port = int(os.getenv("PORT"))
password = os.getenv("PASSWORD")

srv.start(addr, port, password)
srv.accept()

import camera

def sender():
	cam = camera.Camera()
	camout = cam.getoutput()

	cam.start()

	while True:
		srv.sendbytes(camout.getframe(), "camera")

def recver():
	while True:
		try:	
			string, tag = srv.recvstr()

			if tag == "command":
				pass # TODO

			print(string, tag)
		except TimeoutError:
			continue
		except Exception:
			raise

from threading import Thread

sendthread = Thread(target=sender, daemon=True)
recvthread = Thread(target=recver, daemon=True)

sendthread.start()
recvthread.start()

input("서버를 종료하려면 아무 키나 누르십시오.")