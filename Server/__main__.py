print("서버를 준비하는 중입니다. 잠시 기다려 주세요.")

import os, sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

addr = "0.0.0.0"
port = int(os.getenv("PORT"))
password = os.getenv("PASSWORD")

from camera import Camera

cam = Camera()
camout = cam.getoutput()

cam.start()

from car import Car

#car = Car()

import cv

cvresult: list[cv.YoloObject] = None

from server import Connection as Server

srv = Server()
srv.start(addr, port, password)

print(f"서버가 {addr}:{port}에서 시작되었습니다.")
print("클라이언트의 접속을 기다리는 중입니다.")

srv.accept()

print("클라이언트와 연결되었습니다.")

def worker():
	while True:  
		srv.send("camera", camout.getframe())

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

			#result = car.execute(cmd)
			#print("실행에 성공했습니다." if result else "실행에 실패했습니다.")   
		elif tag == "vision":
			json = srv.recvstr()
			print(f"감지 결과: {json}")

			cvresult = cv.fromjson(json)
		else:
			raise Exception(f"Unknown tag '{tag}'")

from threading import Thread

workthread = Thread(target=worker, daemon=True)
recvthread = Thread(target=recver, daemon=True)

workthread.start()
recvthread.start()

input("서버를 종료하려면 아무 키나 누르십시오.")