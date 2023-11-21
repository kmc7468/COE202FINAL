import os
import sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

# import client
# import getpass

# clt = client.Connection()

# addr = input("Address: ")
# port = int(input("Port: "))

# while True:
# 	try:
# 		clt.connect(addr, port, getpass.getpass("Password: "))

# 		break
# 	except Exception as e:
# 		print(f"Connection failed: {e}")

# clt.startrecvstr(print)

# while True:
# 	clt.sendstr(input())

import assistant

ass = assistant.Assistant()

while True:
	try:
		kor = input("한국어: ")
		fml = ass.send(kor)
		print(f"결과:\n{fml}\n")
	except Exception as e:
		print(f"에러: {e}")