import RPi.GPIO as GPIO
import time
import random
from Lab6Shifter import Shifter

class Bug:

    def __init__(self, timestep: float = 0.1, x = 3, isWrapOn = False):
        
        self.timestep  = timestep
        self.x         = x
        self.isWrapOn  = isWrapOn
        self.__running = False
        self.__shifter = Shifter(serialPin=23, clockPin=25, latchPin=24)

    def start(self):
        self.__running = True
        try:
            while self.__running:
                pattern = 1 << self.x
                self.__shifter.shiftByte(pattern)

                self.x += random.choice([-1, 1])

                if self.isWrapOn:
                    self.x %= 8
                else:
                    if self.x < 0:
                        self.x = 0
                    if self.x > 7:
                        self.x = 7

                time.sleep(self.timestep)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.__running = False
        self.__shifter.shiftByte(0)
        GPIO.cleanup()