import time

import RPi.GPIO as GPIO

class SingleServoJoint:
    maxAngle = 0  
    minAngle = 0
    angleShift = 0
    angle = 0
    servo = None


    def __init__(self, servoPin, minAngle, maxAngle, angleShift):
        self.minAngle = minAngle
        self.angleShift = angleShift
        self.maxAngle = maxAngle

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servoPin, GPIO.OUT)

        self.servo = GPIO.PWM(servoPin, 50)  # 50Hz frequency
        self.servo.start(0)


    def zero(self):
        self.move_to_angle(0)
        print("Moving to zero position")


    def move_to_angle(self, targetAngle):

        #if targetAngle < self.minAngle or targetAngle > self.maxAngle:
        #    raise ValueError("Target angle is out of bounds")

        targetAngle += self.angleShift # Adjust target angle by the angle shift

        duty_cycle = 2 + (targetAngle / 18)  # Convert angle to duty cycle
        #print(duty_cycle)
        self.servo.ChangeDutyCycle(duty_cycle)

    def getMinAngle(self):
        return self.minAngle
    
    def getMaxAngle(self):
        return self.maxAngle
       
    def stop(self):
        self.servo.ChangeDutyCycle(0)