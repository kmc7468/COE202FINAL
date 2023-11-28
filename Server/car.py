import modi
import time

bundle = modi.MODI()
motor = bundle.motors[0]
motor2 = bundle.motors[1]

while True:
	motor2.degree = (90, 90)
	motor.speed = (-36, 35)
	time.sleep(2)
	motor2.degree = (45, 45)
	motor.speed = (36, -35)
	time.sleep(2)


# import modi
# import time

# time90Degree = 0.45 # 90도 회전하는데 걸리는 초

# bundle = modi.MODI()
# #bundle = modi.MODI(conn_type="ble", network_uuid="30831ACC")
# motor = bundle.motors[0]

# def disableMotor():
# 	motor.speed = (0, 0)

# def rotateLeft(): #rotate to the left by 10 degrees
# 	motor.speed = (18, 18)
# 	time.sleep(0.35)
# 	disableMotor()

# def rotateRight(): #rotate to the left by 10 degrees
# 	motor.speed = (-18, -18)
# 	time.sleep(0.35)
# 	disableMotor()


# def forward():
# 	motor.speed = (-36, 35)
# 	time.sleep(1.8)
# 	disableMotor()

# def detected(color): #returns whether the box is detected in the middle of the camera
# 	pass

# def position(color): #returns 2D coordinates of the box
# 	pass

# while not detected(color):
# 	rotateLeft()
# forward()
# if position(color)[0]<-20:
# 	while not detected(color):
# 		rotateRight()
# elif position(color[0])>20:
# 	while not detected(color):
# 		rotateLeft()

