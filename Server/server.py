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
		self.__password = password

		self.__serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__serversocket.bind((host, port))
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

	def __handshake(self) -> bool:
		try:
			iv = secrets.token_bytes(16)
			mycipher = cipher.AES256Cipher(self.__password, iv)
			problem = secrets.token_bytes(random.randint(256, 512))

			self._send(iv, encrypt=False)
			self._send(mycipher.encrypt(problem), encrypt=False)

			result = self._recv(decrypt=False) == hashlib.sha3_512(problem).digest()
			if result:
				self._setcipher(mycipher)
				self._send(b"OK", encrypt=False)
			else:
				self._send(b"BYE", encrypt=False)

			return result
		except:
			return False