import modi
import time

def parsecmd(cmd: str) -> list[list[str]]:
	lines = cmd.split("\n")

	return [line.split(" ") for line in lines]

class Car:
	def __init__(self):
		self.__bundle = modi.MODI()
		self.__wheels = self.__bundle.motors[0]
		self.__arms = self.__bundle.motors[1]

	def execute(self, cmd: str) -> bool:
		commands = parsecmd(cmd)

		if commands[0]=="move" and commands[1]=="forward":
			for i in range(int(commands[2])):
				self.forward()
				time.sleep(0.5)
			return True

		return False # returns whether the command is successully executed
			
	def disableMotor(self):
		self.__wheels.speed = (0, 0)

	def forward(self):
		self.__wheels.speed = (-45, 45)
		time.sleep(1)
		self.disableMotor()