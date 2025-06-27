import time

import RPi.GPIO as GPIO

class DoubleServoJoint:
    maxAngle = 0  
    minAngle = 0
    angleShiftL = 0
    angleShiftR = 0
    angle = 0
    servoL = None
    servoR = None


    def __init__(self, servoPinL, servoPinR, minAngle, maxAngle, angleShiftL, angleShiftR):
        self.minAngle = minAngle
        self.angleShiftL = angleShiftL
        self.angleShiftR = angleShiftR
        self.maxAngle = maxAngle

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servoPinL, GPIO.OUT)
        GPIO.setup(servoPinR, GPIO.OUT)

        self.servoL = GPIO.PWM(servoPinL, 50)
        self.servoR = GPIO.PWM(servoPinR, 50)
        self.servoL.start(0)
        self.servoR.start(0)


    def zero(self):
        self.move_to_angle(0)
        print("Moving to zero position")


    def move_to_angle(self, targetAngle):

        if targetAngle < self.minAngle or targetAngle > self.maxAngle:
            raise ValueError("Target angle is out of bounds")

        targetAngleR = targetAngle + self.angleShiftR # Adjust target angle by the angle shift
        targetAngleL = self.angleShiftL - targetAngle # Adjust target angle by the angle shift

        duty_cycleR = 2 + (targetAngleR / 18)  # Convert angle to duty cycle
        duty_cycleL = 2 + (targetAngleL / 18)  # Convert angle to duty cycle

        self.servoR.ChangeDutyCycle(duty_cycleR)
        self.servoL.ChangeDutyCycle(duty_cycleL)

    def getMinAngle(self):
        return self.minAngle    
    
    def getMaxAngle(self):
        return self.maxAngle
       
    def stop(self):
        self.servoL.ChangeDutyCycle(0)
        self.servoR.ChangeDutyCycle(0)