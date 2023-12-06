# 테스트 목적으로 Server를 구동해야 하는 경우 사용하는 파일입니다.
# 라즈베리파이가 아닌 일반 PC에서 구동할 수 있습니다.
print("서버를 준비하는 중입니다. 잠시 기다려 주세요.")

# 경로 설정
import os, sys

sys.path.append(os.path.abspath("./Common"))

# 의존성 해결
from subprocess import check_call

check_call([sys.executable, "-m", "pip", "install", "-r", "./Server/requirements.test.txt"])

# 환경 변수 설정
ADDR = "localhost" # 외부에서의 접근이 필요하다면 0.0.0.0을 사용해야 함
PORT = 12345
PASSWORD = "test"

# 카메라 실행
import cv2

cam = cv2.VideoCapture(0)

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
from car import CarTest

car = CarTest(cvpipe) # MODI와 연결하려면 Car를 사용해야 함

# 클라이언트로부터의 수신 시작
from threading import Condition, Thread

ready = Condition()

def recver():
	import socket

	while True:
		try:
			tag = srv.recvstr()
		except socket.timeout:
			continue

		if tag == "ready":
			with ready:
				ready.notify()
		elif tag == "command":
			car.execute(srv.recvstr()) 
		elif tag == "vision":
			cvpipe.setresult(cv.fromjson(srv.recvstr()))
		else:
			raise Exception(f"Unknown tag '{tag}'")

recvthread = Thread(target=recver, daemon=True)
recvthread.start()

# 작업 시작
def worker():
	with ready:
		ready.wait()

	while True:
		_, frame = cam.read()
		_, jpg = cv2.imencode(".jpg", frame)

		srv.send("camera", bytes(jpg))

workthread = Thread(target=worker, daemon=True)
workthread.start()

print("서버가 준비되었습니다.")
input("서버를 종료하려면 아무 키나 누르십시오.")