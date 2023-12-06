import modi
import time
import cv

def parsecmd(cmd: str) -> list[list[str]]:
	lines = cmd.split("\n")
	return [line.split(" ") for line in lines]

def detected(obj): #returns whether object is detected in the middle
	pos = position(obj)
	if pos==False:
		return False
	return 300<pos<340

def position(obj, var, condition): #returns x coordinates of the object, or False if not detected
	with condition:
		condition.wait()

		for asdf in var:
			if asdf.name == var:
				return asdf.location[0]
		return None

class Car:
	def __init__(self, cvresult, condition):
		self.__bundle = modi.MODI()
		self.__wheels = self.__bundle.motors[0]
		self.__arms = self.__bundle.motors[1]
		self.__ir1 = self.__bundle.irs[0]
		self.__ir2 = self.__bundle.irs[1]
		self.__arms.speed = (0,0)
		self.__wheels.speed = (0,0)
		self.gyro = self.__bundle.gyros[0]
		dummy = self.gyro.yaw
		self.__cvresult = cvresult
		self.__condition = condition

	def execute(self, cmd: str) -> bool:
		commands = parsecmd(cmd)

		for command in commands:
			if command[0]=="move":
				if command[1]=="forward":
					for i in range(int(command[2])):
						self.forward()
						time.sleep(0.5)
				elif command[1]=="back":
					for i in range(int(command[2])):
						self.back()
						time.sleep(0.5)
				elif command[1]=="right":
					self.__wheels.speed = (-35, -35)
					time.sleep(3.1)
					self.disableMotor()
					for i in range(int(command[2])):
						self.forward()
						time.sleep(0.5)
				elif command[1]=="left":
					self.__wheels.speed = (35, 35)
					time.sleep(3.1)
					self.disableMotor()
					for i in range(int(command[2])):
						self.forward()
						time.sleep(0.5)

			if command[0]=="find":
				self.bring(command[1])

		return True # returns whether the command is successully executed
			
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
		current = self.gyro.yaw
		self.__wheels.speed = (50, 50)
		delta = self.convert(self.gyro.yaw - current)
		while True:
			delta = self.convert(self.gyro.yaw - current)
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
		while not detected(obj):
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