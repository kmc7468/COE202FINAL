import cipher
import connection
import hashlib
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
		self.__serversocket.listen(1)
		self.__serversocket.settimeout(1)

	def accept(self):
		while True:
			try:
				clientsocket, clientaddr = self.__serversocket.accept()
				clientsocket.settimeout(1)
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
		try:
			mycipher = self._getcipher()
			problem = secrets.token_bytes(random.randint(256, 512))

			self._send(mycipher.getiv(), encrypt=False)
			self._send(mycipher.encrypt(problem), encrypt=False)

			result = self._recv(decrypt=False) == hashlib.sha3_512(problem).digest()
			self._send(b"OK" if result else b"BYE", encrypt=False)

			return result
		except:
			return False