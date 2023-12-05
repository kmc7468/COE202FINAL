import collections
import socket
import typing

class Connection:
	def __init__(self):
		self.__sendqueue = collections.deque()

	def __del__(self):
		if hasattr(self, "__socket") and self.__socket is not None:
			self.__socket.close()
			del self.__socket

		if hasattr(self, "__cipher"):
			del self.__cipher

	def _setsocket(self, socket: socket):
		self.__socket = socket

	def _getcipher(self):
		return self.__cipher

	def _setcipher(self, cipher):
		self.__cipher = cipher

	def send(self, tag: str, data: typing.Union[str, bytes], flush: bool = True):
		self.__sendqueue.append((tag, data))

		if flush:
			self.sendflush()

	def sendflush(self):
		try:
			tag, data = self.__sendqueue.popleft()
		except IndexError:
			return

		self._send(tag.encode("utf-8"))

		if type(data) is str:
			self._send(data.encode("utf-8"))
		elif type(data) is bytes:
			self._send(data)

	def _send(self, data: bytes, encrypt: bool = True):
		if encrypt:
			self._send(self.__encrypt(data), encrypt=False)
		else:
			self.__socket.sendall(len(data).to_bytes(4, "big"))
			self.__socket.sendall(data)

	def recvstr(self) -> str:
		return self._recv().decode("utf-8")

	def recvbytes(self) -> bytes:
		return self._recv()

	def _recv(self, decrypt: bool = True) -> bytes:
		size = int.from_bytes(self.__recvraw(4), "big")
		data = self.__recvraw(size)

		if decrypt:
			return self.__decrypt(data)
		else:
			return data

	def __recvraw(self, size: int) -> bytes:
		data = b""

		while len(data) < size:
			data += self.__socket.recv(size - len(data))

		return data

	def __encrypt(self, data: bytes) -> bytes:
		return self.__cipher.encrypt(data)

	def __decrypt(self, edata: bytes) -> bytes:
		return self.__cipher.decrypt(edata)