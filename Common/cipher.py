from Crypto.Cipher import AES
import hashlib

# AES-256에서는 블록의 크기가 16바이트입니다.
BLOCK_SIZE = 16

class AES256Cipher:
	def __init__(self, key: str | bytes, iv: bytes):
		if type(key) is str:
			self.__key = hashlib.sha256(key.encode("utf-8")).digest()
		else:
			self.__key = key
		
		self.__iv = iv

	def encrypt(self, data: bytes) -> bytes:
		return AES.new(self.__key, AES.MODE_CBC, self.__iv).encrypt(self.__pad(data))

	def decrypt(self, edata: bytes) -> bytes:
		return self.__unpad(AES.new(self.__key, AES.MODE_CBC, self.__iv).decrypt(edata))

	def __pad(self, data: bytes) -> bytes:
		padlen = BLOCK_SIZE - len(data) % BLOCK_SIZE
		return data + bytes([padlen] * padlen)

	def __unpad(self, data: bytes) -> bytes:
		return data[:-ord(data[len(data)-1:])]