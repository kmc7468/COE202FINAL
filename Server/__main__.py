import os
import sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

import server

srv = server.Connection()

addr = "localhost"
port = int(os.getenv("PORT"))
password = os.getenv("PASSWORD")

srv.start(addr, port, password)
srv.accept()

srv.startrecvstr(print)

while True:
	srv.sendstr(input())