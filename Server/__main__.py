import json
from collections import deque
import os, sys
sys.path.append(os.path.abspath("./Common"))
from dotenv import load_dotenv

yoloList = list()
load_dotenv()

addr = "0.0.0.0"
port = int(os.getenv("PORT"))
password = os.getenv("PASSWORD")

from server import Connection as Server

srv = Server()
srv.start(addr, port, password)

print(f"서버가 {addr}:{port}에서 시작되었습니다.")
print("클라이언트의 접속을 기다리는 중입니다.")

srv.accept()

print("클라이언트와 연결되었습니다.")

queue = deque([])

def sender():
	while True:
		srv.sendflush()

def worker():
	from camera import Camera

	cam = Camera()
	camout = cam.getoutput()

	cam.start()

	while True:  
		srv.sendbytes("camera", camout.getframe())

def recver():
	global yoloList
	import car
	import socket


	mycar = car.Car()

	while True:
		try:
			tag = srv.recvstr()
		except socket.timeout:
			continue

# String을 List로 바꾸기 
		if tag == "command":
			cmd = srv.recvstr()
#    data 
			print(f"실행 요청: {cmd}")

			result = mycar.execute(cmd)
			print("실행에 성공했습니다." if result else "실행에 실패했습니다.")
   
		elif tag == 'yololist':
			yolo = srv.recvstr()
			yoloList = json.loads(yolo)
			print(yoloList)
   
		else:
			raise Exception(f"Unknown tag '{tag}'")

from threading import Thread

sendthread = Thread(target=sender, daemon=True)
workthread = Thread(target=worker, daemon=True)
recvthread = Thread(target=recver, daemon=True)

sendthread.start()
workthread.start()
recvthread.start()

input("서버를 종료하려면 아무 키나 누르십시오.")