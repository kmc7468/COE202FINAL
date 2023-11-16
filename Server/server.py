import cipher
import connection
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

		while True:
			clientsocket, clientaddr = self.__serversocket.accept()
			self._setsocket(clientsocket)

			print(f"{clientaddr}가 접속을 시도했습니다.")

			if self.__handshake():
				print("Handshake에 성공했습니다.")

				break
			else:
				clientsocket.close()
				self._setsocket(None)

				print("Handshake에 실패했습니다.")

	def __initcipher(self, password: str):
		self.__iv = secrets.token_bytes(16)
		self._setcipher(cipher.AES256Cipher(password, self.__iv))

	def __handshake(self) -> bool:
		tempkey = secrets.token_bytes(32)
		tempcipher = cipher.AES256Cipher(tempkey, self.__iv)

		problem = secrets.token_bytes(128)
		self._send(self.__iv, encrypt=False)
		self._send(tempkey, encrypt=False)
		self._send(self._encrypt(problem), encrypt=False)

		answer = tempcipher.decrypt(self._recv(decrypt=False))
		if answer == problem:
			self._send(b"OK", encrypt=False)

			return True
		else:
			self._send(b"BYE", encrypt=False)

			return False