import cv
import server
import threading
import time
import typing

def parsecmd(cmd: str) -> list[list[str]]:
	lines = cmd.split("\n")
	cmds = [line.split(" ") for line in lines]

	try:
		for cmd in cmds:
			if cmd[0] == "move":
				if cmd[1] == "others":
					return None
			elif cmd[0] == "bring":
				if cmd[1] == "others":
					return None
			else:
				return None
	except:
		return None
	else:
		return cmds

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
		if commands is None:
			return False

		for command in commands:
			if command[0] == "move":
				print(f"이동합니다: {command[1]} {command[2]}")
			elif command[0] == "bring":
				print(f"가져옵니다: {command[1]}")

				result = findobject(self.__cvpipe, command[1])
				if result is not None:
					print(f"결과: {result.location} {result.confidence}")
				else:
					print(f"가져오지 못했습니다.")

					return False

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
		if commands is None:
			return False

		for command in commands:
			if command[0]=="move":
				if command[1] == "forward":
					for _ in range(int(command[2])):
						self.forward()
						time.sleep(0.5)
				elif command[1] == "backward":
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
			elif command[0]=="bring":
				self.bring(command[1])

		return True

	def disableMotor(self):
		self.__wheels.speed = (0, 0)

	def forward(self):
		self.__wheels.speed = (-70, 60)
		time.sleep(0.7)
		self.disableMotor()

	def back(self):
		self.__wheels.speed = (60, -60)
		time.sleep(0.7)
		self.disableMotor()
	
	def rotateLeft(self): #rotate to the left by ~10 degrees
		self.__wheels.speed = (35, 35)
		time.sleep(0.4)
		self.disableMotor()

	def rotateRight(self): #rotate to the right by ~10 degrees
		self.__wheels.speed = (-35, -35)
		time.sleep(0.7)
		self.disableMotor()


	def turnAround(self):
		current = self.__gyro.yaw
		self.__wheels.speed = (50, 50)
		while True:
			delta = normalizeangle(self.__gyro.yaw - current)
			#print(delta)
			if 155<delta:
				break
		self.disableMotor()

	def close(self): #returns whether object is close enough to object
		pr1 = self.__ir1.proximity
		pr2 = self.__ir2.proximity
		print(f"1: {pr1} 2: {pr2}")
		return pr1>11 or pr2>11
	
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
			if result is not None and 260<result.location[0]<380:
				break
			self.rotateLeft()
			time.sleep(0.5)

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
			self.__srv.send("command", "fail")

			raise
		else:
			self.__srv.send("command", "success" if result else "fail")
		finally:
			self.__thread = None