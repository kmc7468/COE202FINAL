import os, sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

from getpass import getpass

addr = input("서버 주소: ")
port = int(input("서버 포트: "))
password = getpass("비밀번호: ")

from client import Connection as Client

clt = Client()
clt.connect(addr, port, password)

from httpserver import HTTPServer

httpsrv = HTTPServer()
httpsrv.start()

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

print("서버와 연결되었습니다.")

import assistant
import stt

ass = assistant.Assistant()
mystt = stt.STT()

while True:
	try:
		input("아무 키나 누르면 녹음을 시작합니다. Ctrl+C를 누르면 클라이언트를 종료합니다.")
		print("3초간 녹음을 시작합니다. 명령을 내려주세요.")

		wav = mystt.record(3, rate=48000)

		print("녹음이 완료되었습니다.")

		with open("record.wav", "wb") as f:
			f.write(wav.getbuffer())

		kor = mystt.stt(wav, "너는 장애인을 돕는 로봇의 음성 인식을 담당하게 될거야. 로봇은 물건을 찾거나, 특정 거리만큼 이동하는 역할을 수행할 수 있어. 사용자는 너에게 관련된 명령을 내릴거고, 너는 그 명령을 텍스트로 잘 변환해주면 돼. 예시는 다음과 같아: '앞으로 10만큼 이동해줘', '스마트폰 찾아줘', '뒤로 10만큼 이동하고 파란 상자를 찾아줘'. 하지만, 이 사용자의 명령이 이 예시들만으로 국한되지는 않아.")
		fml = ass.send(kor)

		print(f"인식 결과: {kor}")
		print(f"번역 결과: {fml}")

		clt.sendstr("command")
		clt.sendstr(fml)
	except Exception as e:
		print(f"에러: {e}")

# input("클라이언트를 종료하려면 아무 키나 누르십시오.")

# httpsrv.stop()