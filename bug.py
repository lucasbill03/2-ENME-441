import RPi.GPIO as GPIO
import time
import random
from Lab6Bug import Bug

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

bug = Bug(timestep=0.1, x=3, isWrapOn=False)

try:
	while True:
		if GPIO.input(17):
			bug.start()
		else:
			bug.stop()
			
		if GPIO.input(27):
			bug.isWrapOn = True
		else:
			bug.isWrapOn = False
		
		if GPIO.input(22):
			bug.timestep = 0.03
		else:
			bug.timestep = 0.10

		time.sleep(0.05)

except KeyboardInterrupt:
	pass
	
finally:
	bug.stop()

	GPIO.cleanup()



