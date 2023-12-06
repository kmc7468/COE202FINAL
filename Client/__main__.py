# 경로 설정
import os, sys

sys.path.append(os.path.abspath("./Common"))
sys.path.append(os.path.abspath("./Client/yolov5"))

# 환경 변수 설정
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT"))
STT_PROMPT_ALICE = os.getenv("STT_PROMPT_ALICE")
STT_PROMPT_COMMAND = os.getenv("STT_PROMOT_COMMAND")

# 리소스 로드
start = open("./Client/Resources/준비되었어요.wav", "rb") # 호출어 인식이 가능한 상태가 되었을 때 재생
ready = open("./Client/Resources/듣고있어요.wav", "rb") # 명령어 인식이 가능한 상태가 되었을 때 재생
progress = open("./Client/Resources/기다려주세요.wav", "rb") # 명령어 분석이 시작되었을 때 재생

# 어시스턴트 실행
from assistant import Assistant

ass = Assistant()

# 마이크 실행
from audio import Audio

audio = Audio()
audio.startrecord(4.0)

# 서버 연결
from client import Connection as Client
from getpass import getpass

clt = Client()

while True:
	try:
		addr = input("서버 주소: ")
		port = int(input("서버 포트: "))
		password = getpass("비밀번호: ")

		clt.connect(addr, port, password)
		print("서버와 연결되었습니다.")

		break
	except Exception as e:
		print(f"서버와 연결하지 못했습니다: {e}")
		print()

print("클라이언트를 준비하는 중입니다. 잠시 기다려 주세요.")

# HTTP 서버 실행
from httpserver import HTTPServer

httpsrv = HTTPServer(PORT)
httpsrv.start()

print(f"HTTP 서버가 localhost:{PORT}에서 시작되었습니다.")

# YOLOv5 실행
from cv import Yolo

yolo = Yolo()
yolo.start(f"http://localhost:{PORT}/camera")

def yoloupdater():
	while True:
		httpsrv.setyoloframe(yolo.getresult().frame)

from threading import Thread

yoloupdatethread = Thread(target=yoloupdater, daemon=True)
yoloupdatethread.start()

print("yolov5가 시작되었습니다.")

# 서버로부터의 수신 시작
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
		elif tag == "vision":
			clt.send("vision", yolo.getresult().tojson())
		else:
			raise Exception(f"Unknown tag '{tag}'")

recvthread = Thread(target=recver, daemon=True)
recvthread.start()

# 작업 시작
def worker():
	playstart = True

	while True:
		if playstart:
			audio.play(start)

			playstart = False

		callwav = audio.getrecord(2.0, sleep=False)
		callkor = audio.stt(callwav, STT_PROMPT_ALICE)
		if "엘리" in callkor or "앨리" in callkor or "리스" in callkor:
			playstart = True
		else:
			continue

		audio.play(ready)
		cmdwav = audio.getrecord(4.0)

		audio.playasync(progress)
		cmdkor = audio.stt(cmdwav, STT_PROMPT_COMMAND)
		print(f"인식 결과: {cmdkor}")

		fml = ass.send(cmdkor)
		print(f"번역 결과: {fml}")

		clt.send("command", fml)

workthread = Thread(target=worker, daemon=True)
workthread.start()

print("클라이언트가 준비되었습니다.")
input("클라이언트를 종료하려면 아무 키나 누르십시오.\n")