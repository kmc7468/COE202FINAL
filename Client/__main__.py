print("클라이언트를 준비하는 중입니다. 잠시 기다려 주세요.")

import os, sys
sys.path.append(os.path.abspath("./Common"))
sys.path.append(os.path.abspath("./Client/yolov5"))

from dotenv import load_dotenv

load_dotenv()

start = open("./Client/Resources/준비되었어요.wav", "rb") # 호출어 인식이 가능한 상태가 되었을 때 재생
ready = open("./Client/Resources/듣고있어요.wav", "rb") # 명령어 인식이 가능한 상태가 되었을 때 재생
progress = open("./Client/Resources/기다려주세요.wav", "rb") # 명령어 분석이 시작되었을 때 재생

from httpserver import HTTPServer

PORT = int(os.getenv("PORT"))

httpsrv = HTTPServer(PORT)
httpsrv.start()

print(f"HTTP 서버가 localhost:{PORT}에서 시작되었습니다.")

from cv import Yolo

yolo = Yolo()
yolo.start(f"http://localhost:{PORT}/camera")

def yoloupdater():
	while True:
		httpsrv.setyoloframe(yolo.getresult().frame)

yoloupdatethread = Thread(target=yoloupdater, daemon=True)
yoloupdatethread.start()

print("yolov5가 시작되었습니다.")

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

def recver():
	import json
	import socket
 
	while True:
		try:
			print("fuck1")
			tag = clt.recvstr()
			print("fuck2")
		except socket.timeout:
			print("fuck3")
			continue

		if tag == "camera":
			httpsrv.setcameraframe(clt.recvbytes())
		elif tag == "vision":
			clt.send("vision", json.dumps(yolo.getresult().objects))
		else:
			raise Exception(f"Unknown tag '{tag}'")

from threading import Thread

recvthread = Thread(target=recver, daemon=True)
recvthread.start()

def worker():
	import assistant
	import audio

	ass = assistant.Assistant()

	myaudio = audio.Audio()
	myaudio.startrecord(4.0)

	playstart = True

	print("클라이언트가 준비되었습니다.")
	print("클라이언트를 종료하려면 아무 키나 누르십시오.")

	while True:
		try:
			if playstart:
				myaudio.play(start)

				playstart = False

			callwav = myaudio.getrecord(2.0, sleep=False)
			callkor = myaudio.stt(callwav, "너는 장애인을 돕는 로봇의 음성 인식을 담당하게 될거야. 사용자는 너를 부를 때 '엘리스'라고 부를거야. '엘리' 또는 '리스'라고 부를 수도 있어.")
			if not ("엘리" in callkor or "앨리" in callkor or "리스" in callkor):
				continue

			myaudio.play(ready)
			cmdwav = myaudio.getrecord(4.0)

			myaudio.playasync(progress)
			cmdkor = myaudio.stt(cmdwav, "너는 장애인을 돕는 로봇의 음성 인식을 담당하게 될거야. 로봇은 물건을 찾거나, 특정 거리만큼 이동하는 역할을 수행할 수 있어. 사용자는 너에게 관련된 명령을 내릴거고, 너는 그 명령을 텍스트로 잘 변환해주면 돼. 예시는 다음과 같아: '앞으로 10만큼 이동해줘', '스마트폰 찾아줘', '뒤로 10만큼 이동하고 파란 상자를 찾아줘'. 하지만, 이 사용자의 명령이 이 예시들만으로 국한되지는 않아.")
			print(f"인식 결과: {cmdkor}")

			fml = ass.send(cmdkor)
			print(f"번역 결과: {fml}")

			clt.send("command", fml)

			playstart = True
		except Exception as e:
			print(f"명령을 처리하지 못했습니다: {e}")

workthread = Thread(target=worker, daemon=True)
workthread.start()

input()