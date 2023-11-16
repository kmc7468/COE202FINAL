import os, sys
sys.path.append(os.path.abspath("./Common"))

from dotenv import load_dotenv

load_dotenv()

#import car

import server

srv = server.Connection()
srv.start("localhost", 1234, "password")
print(srv.recvstr())
srv.sendstr("Bye, world!")