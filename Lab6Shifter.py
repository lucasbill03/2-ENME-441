import RPi.GPIO as GPIO
import time

## self will be the reference to the instance of the class
class Shifter:

    ## Initializer for the Shifter class, field values set to the
    ## serialPin, clockPin, and latchPin values
    def __init__(self, serialPin, clockPin, latchPin):
        
        self.serialPin = serialPin
        self.clockPin = clockPin
        self.latchPin = latchPin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.serialPin, GPIO.OUT)
        GPIO.setup(self.clockPin, GPIO.OUT, initial=0)
        GPIO.setup(self.latchPin, GPIO.OUT, initial=0)

    def __ping(self, pin):
        GPIO.output(pin, 1)
        time.sleep(0)
        GPIO.output(pin, 0)

    def shiftByte(self, byte):

        for i in range(8):
            GPIO.output(self.serialPin, (byte >> i) & 1)
            self.__ping(self.clockPin)

        self.__ping(self.latchPin)