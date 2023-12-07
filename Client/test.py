# 테스트 목적으로 Client를 구동해야 하는 경우 사용하는 파일입니다.
print("클라이언트를 준비하는 중입니다. 잠시 기다려 주세요.")

# 경로 설정
import os, sys

sys.path.append(os.path.abspath("./Common"))
sys.path.append(os.path.abspath("./Client/yolov5"))

# 의존성 해결
from subprocess import check_call

check_call([sys.executable, "-m", "pip", "install", "-r", "./Client/requirements.test.txt"])

# 환경 변수 설정
ADDR = "localhost"
PORT = 12345
PASSWORD = "test"

HTTP_PORT = 12342

# 리소스 로드
start = open("./Client/Resources/준비되었어요.wav", "rb") # 호출어 인식이 가능한 상태가 되었을 때 재생
ready = open("./Client/Resources/듣고있어요.wav", "rb") # 명령어 인식이 가능한 상태가 되었을 때 재생
progress = open("./Client/Resources/기다려주세요.wav", "rb") # 명령어 분석이 시작되었을 때 재생

# 서버 연결
from client import Connection as Client

clt = Client()

while True:
	try:
		clt.connect(ADDR, PORT, PASSWORD)
		print("서버와 연결되었습니다.")

		break
	except Exception as e:
		print(f"서버와 연결하지 못했습니다: {e}")

# HTTP 서버 실행
from httpserver import HTTPServer

httpsrv = HTTPServer(HTTP_PORT)
httpsrv.start()

print(f"HTTP 서버가 localhost:{HTTP_PORT}에서 시작되었습니다.")

# YOLOv5 실행
from cv import Yolo

yolo = Yolo()
yolo.start("http://localhost:12342/camera")

def yoloupdater():
	while True:
		httpsrv.setyoloframe(yolo.getresult().frame)

from threading import Condition, Thread

yoloupdatethread = Thread(target=yoloupdater, daemon=True)
yoloupdatethread.start()

print("YOLOv5가 시작되었습니다.")

# 서버로부터의 수신 시작
carresult = None
carresultcondition = Condition()

clt.send("ready", None)

def recver():
	import socket

	while True:
		try:
			tag = clt.recvstr()
		except socket.timeout:
			continue

		if tag == "camera":
			httpsrv.setcameraframe(clt.recvbytes())
		elif tag == "command":
			global carresult

			with carresultcondition:
				carresult = clt.recvstr()
				carresultcondition.notify()
		elif tag == "vision":
			clt.send("vision", yolo.getresult().tojson())
		else:
			raise Exception(f"Unknown tag '{tag}'")

recvthread = Thread(target=recver, daemon=True)
recvthread.start()

# 작업 시작
print("클라이언트가 준비되었습니다.")
print("클라이언트를 종료하려면 Ctrl+C를 누르십시오.")

while True:
	cmd = input("명령어: ")
	clt.send("command", cmd)

	with carresultcondition:
		carresultcondition.wait()

		print(f"결과: {carresult}")