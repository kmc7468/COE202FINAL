import cv
import server
import threading
import time
import typing

def parsecmd(cmd: str) -> list[list[str]]:
	lines = cmd.split("\n")
	return [line.split(" ") for line in lines]

def normalizeangle(angle: int) -> int:
	return (angle + 180) % 360 - 180

def findobject(cvpipe: cv.Pipe, name: str) -> cv.Object:
	result = cvpipe.getresult()

	for object in result.objects:
		if object.name == name:
			return object
	else:
		return None

class CarTest:
	def __init__(self, cvpipe: cv.Pipe):
		self.__cvpipe = cvpipe

	def execute(self, cmd: str) -> bool:
		commands = parsecmd(cmd)

		for command in commands:
			if command[0] == "move":
				print(f"이동합니다: {command[1]} {command[2]}")
			elif command[0] == "find":
				print(f"찾습니다: {command[1]}")

				result = findobject(self.__cvpipe, command[1])
				if result is not None:
					print(f"결과: {result.location} {result.confidence}")
				else:
					print(f"찾지 못했습니다.")

		time.sleep(2)

		return True

class Car:
	def __init__(self, cvpipe: cv.Pipe):
		from modi import MODI

		self.__bundle = MODI()
		self.__wheels = self.__bundle.motors[0]
		self.__arms = self.__bundle.motors[1]
		self.__ir1 = self.__bundle.irs[0]
		self.__ir2 = self.__bundle.irs[1]
		self.__gyro = self.__bundle.gyros[0]

		self.__wheels.speed = (0, 0)
		self.__arms.speed = (0, 0)
		_ = self.__gyro.yaw

		self.__cvpipe = cvpipe

	def execute(self, cmd: str) -> bool:
		commands = parsecmd(cmd)

		for command in commands:
			if command[0]=="move":
				if command[1] == "forward":
					for _ in range(int(command[2])):
						self.forward()
						time.sleep(0.5)
				elif command[1] == "back":
					for _ in range(int(command[2])):
						self.back()
						time.sleep(0.5)
				elif command[1] == "right":
					self.__wheels.speed = (-35, -35)
					time.sleep(3.1)
					self.disableMotor()
					for _ in range(int(command[2])):
						self.forward()
						time.sleep(0.5)
				elif command[1] == "left":
					self.__wheels.speed = (35, 35)
					time.sleep(3.1)
					self.disableMotor()
					for _ in range(int(command[2])):
						self.forward()
						time.sleep(0.5)
			elif command[0]=="find":
				self.bring(command[1])

		return True

	def bring(self,obj):
		result = detected(obj, self.__cvresult, self.__condition)
		print(f"탐지 결과 {result}")

		while not detected(obj, self.__cvresult, self.__condition):
			self.rotateLeft()

		forward_time=0
		while not self.close():
			self.forward()
			forward_time+=1

		self.grab()
		self.turnAround()
		for i in range(forward_time):
			self.forward()

		self.ungrab()
		self.turnAround()

	def disableMotor(self):
		self.__wheels.speed = (0, 0)

	def forward(self):
		self.__wheels.speed = (-60, 60)
		time.sleep(0.7)
		self.disableMotor()

	def back(self):
		self.__wheels.speed = (60, -60)
		time.sleep(0.7)
		self.disableMotor()
	
	def rotateLeft(self): #rotate to the left by ~10 degrees
		self.__wheels.speed = (35, 35)
		time.sleep(0.7)
		self.disableMotor()

	def rotateRight(self): #rotate to the right by ~10 degrees
		self.__wheels.speed = (-35, -35)
		time.sleep(0.7)
		self.disableMotor()

	def convert(self,angle):
		return (angle+180)%360-180

	def turnAround(self):
		current = self.__gyro.yaw
		self.__wheels.speed = (50, 50)
		delta = self.convert(self.__gyro.yaw - current)
		while True:
			delta = self.convert(self.__gyro.yaw - current)
			print(delta)
			if 155<delta:
				break
		self.disableMotor()

	def close(self): #returns whether object is close enough to object
		return self.__ir1.proximity>11 or self.__ir2.proximity>11
	
	def grab(self):
		self.__arms.speed = (30, -28)
		time.sleep(0.83)
		self.__arms.speed = (0,0)

	def ungrab(self):
		self.__arms.speed = (-30, 28)
		time.sleep(1.1)
		self.__arms.speed = (0,0)

	def bring(self,obj):
		while True:
			result=findobject(self.__cvpipe, obj)
			if result is not None and 280<result.location[0]<360:
				break
			self.rotateLeft()

		forward_time=0
		while not self.close():
			self.forward()
			forward_time+=1

		self.grab()
		self.turnAround()
		for i in range(forward_time):
			self.forward()

		self.ungrab()
		self.turnAround()

class Executor:
	def __init__(self, car: typing.Union[Car, CarTest], srv: server.Connection):
		self.__car = car
		self.__srv = srv

		self.__thread = None
	
	def execute(self, cmd: str):
		if self.__thread is None:
			self.__thread = threading.Thread(target=self.__execute, args=(cmd,), daemon=True)
			self.__thread.start()
		else:
			self.__srv.send("command", "busy")

	def __execute(self, cmd: str):
		try:
			result = self.__car.execute(cmd)
		except:
			self.__srv.send("command", "error")

			raise
		else:
			self.__srv.send("command", "success" if result else "fail")
		finally:
			self.__thread = None