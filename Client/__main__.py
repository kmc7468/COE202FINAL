import os
import sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

import client
import getpass

clt = client.Connection()

addr = input("Address: ")
port = int(input("Port: "))

while True:
	try:
		clt.connect(addr, port, getpass.getpass("Password: "))

		break
	except Exception as e:
		print(f"Connection failed: {e}")

def sender():
	import assistant
	import stt

	ass = assistant.Assistant()
	mystt = stt.STT()

	while True:
		try:
			input("아무 키나 누르면 녹음을 시작합니다.")
			print("3초간 녹음을 시작합니다. 명령을 내려주세요.")

			wav = mystt.record(3, rate=48000)

			print("녹음이 완료되었습니다.")

			with open("record.wav", "wb") as f:
				f.write(wav.getbuffer())

			kor = mystt.stt(wav, "너는 장애인을 돕는 로봇의 음성 인식을 담당하게 될거야. 로봇은 물건을 찾거나, 특정 거리만큼 이동하는 역할을 수행할 수 있어. 사용자는 너에게 관련된 명령을 내릴거고, 너는 그 명령을 텍스트로 잘 변환해주면 돼. '앞으로 10만큼 이동해줘', '스마트폰 찾아줘', '뒤로 10만큼 이동하고 파란 상자를 찾아줘' 등의 명령이 입력될거야.")
			fml = ass.send(kor)

			print(f"인식 결과: {kor}")
			print(f"번역 결과: {fml}")

			clt.sendstr(fml, "command")
		except Exception as e:
			print(f"에러: {e}")

def recver():
	while True:
		try:	
			data, tag = clt.recvbytes()

			if tag == "camera":
				pass # TODO

			print(data, tag)
		except TimeoutError:
			continue
		except Exception:
			raise

from threading import Thread

recvthread = Thread(target=recver, daemon=True)

recvthread.start()

sender()