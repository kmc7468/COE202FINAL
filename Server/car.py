import modi

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

		# TODO: parse command and do something
		return False # returns whether the command is successully executed