import os, sys
sys.path.append(os.path.abspath("./Common"))

import dotenv

dotenv.load_dotenv()

addr = "localhost"
port = int(os.getenv("PORT"))
password = os.getenv("PASSWORD")

import server

srv = server.Connection()
srv.start(addr, port, password)

print(f"서버가 {addr}:{port}에서 시작되었습니다.")
print("클라이언트의 접속을 기다리는 중입니다.")

srv.accept()

def sender():
	import camera

	cam = camera.Camera()
	camout = cam.getoutput()

	cam.start()

	while True:
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