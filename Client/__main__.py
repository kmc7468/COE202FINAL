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
input("클라이언트를 종료하려면 아무 키나 누르십시오.")