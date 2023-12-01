# 테스트 목적으로 Server를 구동해야 하는 경우 사용하는 파일입니다.
# 라즈베리파이가 아닌 일반 PC에서 구동할 수 있습니다.

import os, sys
sys.path.append(os.path.abspath("./Common"))

addr = "localhost"
port = 12345
password = "test"

from server import Connection as Server

srv = Server()
srv.start(addr, port, password)

print(f"서버가 {addr}:{port}에서 시작되었습니다.")
print("클라이언트의 접속을 기다리는 중입니다.")

srv.accept()

print("클라이언트와 연결되었습니다.")

def sender():
	import cv2

	cam = cv2.VideoCapture(0)

	while True:
		_, frame = cam.read()
		_, jpg = cv2.imencode(".jpg", frame)

		srv.sendstr("camera")
		srv.sendbytes(bytes(jpg))

def recver():
	import socket

	while True:
		try:
			tag = srv.recvstr()
		except socket.timeout:
			continue

		if tag == "command":
			cmd = srv.recvstr()
			print(f"실행 요청: {cmd}")
		else:
			raise Exception(f"Unknown tag '{tag}'")

from threading import Thread

sendthread = Thread(target=sender, daemon=True)
recvthread = Thread(target=recver, daemon=True)

sendthread.start()
recvthread.start()

input("서버를 종료하려면 아무 키나 누르십시오.")