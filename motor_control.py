import time
from adafruit_servokit import ServoKit

class Dog:
    def __init__(self):
        self.kit = ServoKit(channels=16)
        self.reset_servos(cam=True)
        
    def reset_servos(self, cam=False):
        max_range = 16 if cam else 14
        for i in range(max_range):
            self.kit.servo[i].angle = 90
            
    def move_forward(self, steps = 10):
        self.reset_servos()
    
        diff = 45
        forward = 90 - diff
        backward = 90 + diff
    
        big_delay = .5
        small_delay = 0
    
        count = 0
        while count < steps:
            count += 1
        
            time.sleep(small_delay)
            self.kit.servo[3].angle = backward
            time.sleep(big_delay)
            self.kit.servo[3].angle = 90
        
            time.sleep(small_delay)
            self.kit.servo[1].angle = backward
            time.sleep(big_delay)
            self.kit.servo[1].angle = 90
        
            time.sleep(small_delay)
            self.kit.servo[7].angle = forward
            time.sleep(big_delay)
            self.kit.servo[7].angle = 90
        
            time.sleep(small_delay)
            self.kit.servo[5].angle = forward
            time.sleep(big_delay)
            self.kit.servo[5].angle = 90
    
        self.reset_servos()
    
    def move_camera(self, pan=0, tilt=0):
        if self.kit.servo[14].angle + tilt >= 0 and self.kit.servo[14].angle + tilt <=180:
            self.kit.servo[14].angle = self.kit.servo[14].angle + tilt
        if self.kit.servo[15].angle + pan >= 90 and self.kit.servo[15].angle + pan <= 180:
            self.kit.servo[15].angle = self.kit.servo[15].angle + pan