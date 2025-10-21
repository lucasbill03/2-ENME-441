import time, RPi.GPIO as GPIO
from Lab6Shifter import Shifter

sh = Shifter(23, 25, 24)
try:

    for i in range(8):

        sh.shiftByte(1 << i)
        time.sleep(0.2)
    sh.shiftByte(0)

    for i in range: 

finally:

    GPIO.cleanup()