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

	cam = Camera()
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
		except socket.timeout:
			continue

		if tag == "command":
			string = srv.recvstr()
			print(string) # TODO
		else:
			raise Exception(f"Unknown tag '{tag}'")

from threading import Thread

sendthread = Thread(target=sender, daemon=True)
recvthread = Thread(target=recver, daemon=True)

sendthread.start()
recvthread.start()

input("서버를 종료하려면 아무 키나 누르십시오.")