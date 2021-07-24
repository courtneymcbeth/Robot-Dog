import time
from adafruit_servokit import ServoKit

class Dog:
    def __init__(self):
        self.kit = ServoKit(channels=16)
        self.reset_servos(cam=True)
        
    def reset_servos(self, cam=False):
        if cam:
            self.kit.servo[14].angle = 90
            self.kit.servo[15].angle = 180
        for i in range(0, 8, 2):
            self.kit.servo[i].angle = 90
            self.kit.servo[i+1].angle = 85
            
    def move_forward(self, steps = 20):
        self.kit.servo[1].angle = 70
        self.kit.servo[3].angle = 70
        
        self.kit.servo[5].angle = 100
        self.kit.servo[7].angle = 100
        
        if steps is not None:
            time.sleep(steps)
            self.stop_moving()
    
    def move_backward(self, steps = 20):
        self.kit.servo[5].angle = 70
        self.kit.servo[7].angle = 70
        
        self.kit.servo[1].angle = 100
        self.kit.servo[3].angle = 100
        
        if steps is not None:
            time.sleep(steps)
            self.stop_moving()
    
    def stop_moving(self):
        for i in range(1, 8, 2):
            self.kit.servo[i].angle = 85
    
    def turn_left(self):
        if self.kit.servo[0].angle >= 10:
            self.kit.servo[0].angle -= 10
        if self.kit.servo[4].angle >= 10:
            self.kit.servo[4].angle -= 10
    
    def turn_right(self):
        if self.kit.servo[0].angle <= 170:
            self.kit.servo[0].angle += 10
        if self.kit.servo[4].angle <= 170:
            self.kit.servo[4].angle += 10
    
    def move_camera(self, pan=0, tilt=0):
        if self.kit.servo[14].angle + tilt >= 0 and self.kit.servo[14].angle + tilt <=180:
            self.kit.servo[14].angle = self.kit.servo[14].angle + tilt
        if self.kit.servo[15].angle + pan >= 90 and self.kit.servo[15].angle + pan <= 180:
            self.kit.servo[15].angle = self.kit.servo[15].angle + pan