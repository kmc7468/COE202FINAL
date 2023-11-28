import os, sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

addr = "localhost"
port = int(os.getenv("PORT"))
password = os.getenv("PASSWORD")

from server import Connection as Server

srv = Server()
srv.start(addr, port, password)

print(f"서버가 {addr}:{port}에서 시작되었습니다.")
print("클라이언트의 접속을 기다리는 중입니다.")

srv.accept()

print("클라이언트와 연결되었습니다.")

def sender():
	from camera import Camera
	import time

	cam = Camera()
	camout = cam.getoutput()

	cam.start()

	INTERVAL = 1.0 / int(os.getenv("FPS"))
	last = None

	while True:
		now = time.time()

		if last is not None:
			sleep = INTERVAL - (now - last)
			if sleep > 0:
				time.sleep(sleep)

		last = now

		srv.sendstr("camera")
		srv.sendbytes(camout.getframe())

def recver():
	import socket

	while True:
		try:
			tag = srv.recvstr()
			print(tag)

			if tag == "command":
				string = srv.recvstr()
				print(string) # TODO
			elif tag == "end":
				exit()
		except socket.timeout:
			continue
		except Exception:
			raise

from threading import Thread

sendthread = Thread(target=sender, daemon=True)
recvthread = Thread(target=recver, daemon=True)

sendthread.start()
recvthread.start()

input("서버를 종료하려면 아무 키나 누르십시오.")