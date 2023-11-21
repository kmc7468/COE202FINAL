import cipher
import connection
import hashlib
import socket

class Connection(connection.Connection):
	def connect(self, host: str, port: int, password: str):
		mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mysocket.connect((host, port))
		mysocket.settimeout(1)

		self._setsocket(mysocket)

		if not self.__handshake(password):
			mysocket.close()
			self._setsocket(None)

			raise Exception("Handshake failed")

	def __handshake(self, password: str):
		mycipher = cipher.AES256Cipher(password, self._recv(decrypt=False))
		problem = mycipher.decrypt(self._recv(decrypt=False))

		self._send(hashlib.sha3_512(problem).digest(), encrypt=False)

		result = self._recv(decrypt=False) == b"OK"
		if result:
			self._setcipher(mycipher)

		return result