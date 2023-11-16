import cipher
import connection
import socket

class Connection(connection.Connection):
	def connect(self, host: str, port: int, password: str):
		mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mysocket.connect((host, port))

		self._setsocket(mysocket)
		self.__handshake(password)

	def __handshake(self, password: str):
		iv = self._recv(decrypt=False)
		mycipher = cipher.AES256Cipher(password, iv)
		self._setcipher(mycipher)

		tempkey = self._recv(decrypt=False)
		tempcipher = cipher.AES256Cipher(tempkey, iv)

		problem = self._decrypt(self._recv(decrypt=False))
		self._send(tempcipher.encrypt(problem), encrypt=False)

		result = self._recv(decrypt=False)
		if result != b"OK":
			raise Exception("Handshake failed")