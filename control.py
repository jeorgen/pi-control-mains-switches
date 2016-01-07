#!/usr/bin/env python
"""

This version by Jorgen Modin, jorgen@webworks.se

This file uses RPi.GPIO to output a bit train to a 433.92 MHz transmitter, allowing you
to control light switches from the Elro & Brennenstuhl brands, and possibly others.

Tested with a Brennenstuhl RCS 1000, on channel (device) 1, device group (key) 1.

Credits:
Based on
"elropi.py" for switching Elro devices using Python on Raspberry Pi
by Heiko H. 2012 at http://pastebin.com/aRipYrZ6

This file is mostly a port from C++ and Wiring to Python and the RPi.GPIO library, based on 
C++ source code written by J. Lukas:
    http://www.jer00n.nl/433send.cpp
and Arduino source code written by Piepersnijder:
    http://gathering.tweakers.net/forum/view_message/34919677
Some parts have been rewritten and/or translated.

This code uses the Broadcom GPIO pin naming by default, which can be changed in the 
"GPIOMode" class variable below. 
For more on pin naming see: http://elinux.org/RPi_Low-level_peripherals

Version 1.0
"""

import time
import RPi.GPIO as GPIO

class RemoteSwitchResource(object):
    def __init__(self, *args, **kwargs):
        self.package_obj = RemoteSwitch(*args, **kwargs)

    def __enter__(self, *args, **kwargs):

                
        
        return self.package_obj

    def __exit__(self, exc_type, exc_value, traceback):
        self.package_obj.cleanup()

class RemoteSwitch(object):
    repeat = 10 # Number of transmissions
    pulselength = 300 # microseconds
    GPIOMode = GPIO.BCM
    
    def __init__(self, device, key=[1,0,0,0,0], pin=17):
        ''' 
        devices: A = 1, B = 2, C = 4, D = 8, E = 16  
        key: according to dipswitches on your Elro/Brennenstuhl receivers
        pin: according to Broadcom pin naming
        '''     
        self.pin = pin 
        self.key = key
        self.device = device
        GPIO.setmode(self.GPIOMode)
        GPIO.setup(self.pin, GPIO.OUT)

    def cleanup():
        GPIO.cleanup()
        
    def switchOn(self):
        self._switch(GPIO.HIGH)

    def switchOff(self):
        self._switch(GPIO.LOW)

    def _switch(self, switch):
        self.bit = [142, 142, 142, 142, 142, 142, 142, 142, 142, 142, 142, 136, 128, 0, 0, 0]       

        for t in range(5):
            if self.key[t]:
                self.bit[t]=136 
        x=1
        for i in range(1,6):
            if self.device & x > 0:
                self.bit[4+i] = 136
            x = x<<1

        if switch == GPIO.HIGH:
            self.bit[10] = 136
            self.bit[11] = 142
                
        bangs = []
        for y in range(16):
            x = 128
            for i in range(1,9):
                b = (self.bit[y] & x > 0) and GPIO.HIGH or GPIO.LOW
                bangs.append(b)
                x = x>>1
                
        GPIO.output(self.pin, GPIO.LOW)
        for z in range(self.repeat):
            for b in bangs:
                GPIO.output(self.pin, b)
                time.sleep(self.pulselength/1000000.)