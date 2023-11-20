from Crypto.Cipher import AES
import hashlib

# AES-256에서는 블록의 크기가 16바이트입니다.
BLOCK_SIZE = 16

class AES256Cipher:
	def __init__(self, key: str | bytes, iv: bytes):
		mykey = key
		if type(key) is str:
			mykey = hashlib.sha256(key.encode("utf-8")).digest()

		self.__iv = iv
		self.__cipher = AES.new(mykey, AES.MODE_CBC, iv)
		self.__decipher = AES.new(mykey, AES.MODE_CBC, iv)

	def getiv(self) -> bytes:
		return self.__iv

	def encrypt(self, data: bytes) -> bytes:
		return self.__cipher.encrypt(self.__pad(data))

	def decrypt(self, edata: bytes) -> bytes:
		return self.__unpad(self.__decipher.decrypt(edata))

	def __pad(self, data: bytes) -> bytes:
		padlen = BLOCK_SIZE - len(data) % BLOCK_SIZE
		return data + bytes([padlen] * padlen)

	def __unpad(self, data: bytes) -> bytes:
		return data[:-ord(data[len(data)-1:])]