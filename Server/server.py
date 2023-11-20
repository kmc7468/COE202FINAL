import cipher
import connection
import random
import secrets
import socket

class Connection(connection.Connection):
	def __del__(self):
		if hasattr(self, "__serversocket"):
			self.__serversocket.close()
			del self.__serversocket

		super().__del__()

	def start(self, host: str, port: int, password: str):
		self.__initcipher(password)

		self.__serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__serversocket.bind((host, port))

		self.__serversocket.settimeout(1)
		self.__serversocket.listen(1)

	def accept(self):
		while True:
			try:
				clientsocket, clientaddr = self.__serversocket.accept()
				self._setsocket(clientsocket)

				print(f"{clientaddr}가 접속을 시도했습니다.")
			except socket.timeout:
				continue

			if self.__handshake():
				print("Handshake에 성공했습니다.")

				break
			else:
				clientsocket.close()
				self._setsocket(None)

				print("Handshake에 실패했습니다.")

	def __initcipher(self, password: str):
		self._setcipher(cipher.AES256Cipher(password, secrets.token_bytes(16)))

	def __handshake(self) -> bool:
		mycipher = self._getcipher()
		self._send(mycipher.getiv(), encrypt=False)

		seedlen = random.randint(128, 256)
		serverseed = secrets.token_bytes(seedlen)
		clientseed = secrets.token_bytes(seedlen)
		self._send(mycipher.encrypt(serverseed), encrypt=False)
		self._send(mycipher.encrypt(clientseed), encrypt=False)

		problem = bytes([(a + b) % 256 for a, b in zip(serverseed, clientseed)])
		answer = mycipher.decrypt(self._recv(decrypt=False))
		if problem == answer:
			self._setrandom(random.Random(serverseed), random.Random(clientseed))
			self._send(b"OK", encrypt=False)

			return True
		else:
			self._send(b"BYE", encrypt=False)

			return False