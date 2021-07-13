import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

def one_leg():
    diff = 45
    forward = 90 - diff
    backward = 90 + diff
    
    big_delay = .5
    small_delay = 0
    
    count = 0
    while count < 5:
        count += 1
        
        time.sleep(small_delay)
        kit.servo[3].angle = backward
        time.sleep(big_delay)
        kit.servo[3].angle = 90
        
        time.sleep(small_delay)
        kit.servo[1].angle = backward
        time.sleep(big_delay)
        kit.servo[1].angle = 90
        
        time.sleep(small_delay)
        kit.servo[7].angle = forward
        time.sleep(big_delay)
        kit.servo[7].angle = 90
        
        time.sleep(small_delay)
        kit.servo[5].angle = forward
        time.sleep(big_delay)
        kit.servo[5].angle = 90
    
    reset_servos()

def reset_servos():
    for i in range(16):
        kit.servo[i].angle = 90
    time.sleep(2)
    print("done")

one_leg()