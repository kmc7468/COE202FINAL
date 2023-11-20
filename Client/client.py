import cipher
import connection
import socket
import random

class Connection(connection.Connection):
	def connect(self, host: str, port: int, password: str):
		mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mysocket.connect((host, port))

		self._setsocket(mysocket)
		self.__handshake(password)

	def __handshake(self, password: str):
		iv = self._recv(decrypt=False)
		mycipher = cipher.AES256Cipher(password, iv)

		serverseed = mycipher.decrypt(self._recv(decrypt=False))
		clientseed = mycipher.decrypt(self._recv(decrypt=False))

		answer = bytes([(a + b) % 256 for a, b in zip(serverseed, clientseed)])
		self._send(mycipher.encrypt(answer), encrypt=False)

		result = self._recv(decrypt=False)
		if result == b"OK":
			self._setcipher(mycipher)
			self._setrandom(random.Random(clientseed), random.Random(serverseed))
		else:
			raise Exception("Handshake failed")