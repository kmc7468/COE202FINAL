import os, sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

import client

clt = client.Connection()
clt.connect("localhost", 1234, "password")
clt.sendstr("Hello, world!")
clt.sendstr("Hello, world!")
print(clt.recvstr())
print(clt.recvstr())