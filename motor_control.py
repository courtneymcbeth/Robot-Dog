import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

count = 0
while count < 10:
    count += 1
    
    kit.servo[1].angle = 30
    kit.servo[2].angle = 120
    time.sleep(1)

    kit.servo[1].angle = 120
    kit.servo[2].angle = 30
    time.sleep(1)
    
kit.servo[1].angle = 90
kit.servo[2].angle = 90