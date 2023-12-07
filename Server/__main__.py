print("서버를 준비하는 중입니다. 잠시 기다려 주세요.")

# 경로 설정
import os, sys

sys.path.append(os.path.abspath("./Common"))

# 환경 변수 설정
from dotenv import load_dotenv

load_dotenv()

ADDR = "0.0.0.0"
PORT = int(os.getenv("PORT"))
PASSWORD = os.getenv("PASSWORD")

# 카메라 실행
from camera import Camera

cam = Camera()
cam.start()

camout = cam.getoutput()

# 서버 실행 및 클라이언트 연결
from server import Connection as Server

srv = Server()
srv.start(ADDR, PORT, PASSWORD)

print(f"서버가 {ADDR}:{PORT}에서 시작되었습니다.")
print("클라이언트의 접속을 기다리는 중입니다.")

srv.accept()

print("클라이언트와 연결되었습니다.")

# CV 파이프 초기화
import cv

cvpipe = cv.Pipe(srv)

# 하드웨어 초기화
from car import Car, Executor as CarExecutor

car = Car(cvpipe)
carexe = CarExecutor(car, srv)

# 클라이언트로부터의 수신 시작
from threading import Condition, Thread

cltready = Condition()

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

			carexe.execute(cmd)
		elif tag == "ready":
			with cltready:
				cltready.notify()
		elif tag == "vision":
			json = srv.recvstr()
			print(f"감지 결과: {json}")

			cvpipe.setresult(cv.fromjson(json))
		else:
			raise Exception(f"Unknown tag '{tag}'")

recvthread = Thread(target=recver, daemon=True)
recvthread.start()

# 작업 시작
def worker():
	with cltready:
		cltready.wait()

	while True:  
		srv.send("camera", camout.getframe())

workthread = Thread(target=worker, daemon=True)
workthread.start()

print("서버가 준비되었습니다.")
input("서버를 종료하려면 아무 키나 누르십시오.\n")