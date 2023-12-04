# 테스트 목적으로 Client를 구동해야 하는 경우 사용하는 파일입니다.

print("클라이언트를 준비하는 중입니다. 잠시 기다려 주세요.")

import os, sys
sys.path.append(os.path.abspath("./Common"))
sys.path.append(os.path.abspath("./Client/yolov5"))

from subprocess import check_call
check_call([sys.executable, "-m", "pip", "install", "-r", "./Client/requirements.test.txt"])

start = open("./Client/Resources/준비되었어요.wav", "rb") # 호출어 인식이 가능한 상태가 되었을 때 재생
ready = open("./Client/Resources/듣고있어요.wav", "rb") # 명령어 인식이 가능한 상태가 되었을 때 재생
progress = open("./Client/Resources/기다려주세요.wav", "rb") # 명령어 분석이 시작되었을 때 재생

from httpserver import HTTPServer

httpsrv = HTTPServer(1234)
httpsrv.start()

print("HTTP 서버가 localhost:1234에서 시작되었습니다.")

from client import Connection as Client

clt = Client()

while True:
	try:
		addr = "localhost"
		port = 12345
		password = "test"

		clt.connect(addr, port, password)
		print("서버와 연결되었습니다.")

		break
	except Exception as e:
		print(f"서버와 연결하지 못했습니다: {e}")

def recver():
	import socket

	while True:
		try:
			tag = clt.recvstr()
		except socket.timeout:
			continue

		if tag == "camera":
			httpsrv.setcameraframe(clt.recvbytes())
		else:
			raise Exception(f"Unknown tag '{tag}'")

from threading import Thread

recvthread = Thread(target=recver, daemon=True)
recvthread.start()

from cv import Yolo

yolo = Yolo()
yolo.start("http://localhost:1234/camera")

def yoloupdater():
	while True:
		httpsrv.setyoloframe(yolo.getresult().frame)

yoloupdatethread = Thread(target=yoloupdater, daemon=True)
yoloupdatethread.start()

print("yolov5가 시작되었습니다.")

print("클라이언트가 준비되었습니다.")
print("클라이언트를 종료하려면 Ctrl+C를 누르십시오.")

while True:
	cmd = input("명령어: ")

	clt.sendstr("command")
	clt.sendstr(cmd)

	print("명령어가 서버로 전송되었습니다.")