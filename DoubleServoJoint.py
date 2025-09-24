import time

#import RPi.GPIO as GPIO
from pigpioFolder import pigpio

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
        self.servoPinL = servoPinL
        self.servoPinR = servoPinR

        self.servoL = pigpio.pi()
        self.servoR = pigpio.pi()
        self.servoL.set_mode(self.servoPinL, pigpio.OUTPUT)
        self.servoR.set_mode(self.servoPinR, pigpio.OUTPUT)

    def zero(self):
        self.move_to_angle(0)
        print("Moving to zero position")


    def move_to_angle(self, targetAngle):

        #if targetAngle < self.minAngle or targetAngle > self.maxAngle:
        #    raise ValueError("Target angle is out of bounds")

        targetAngleR = targetAngle + self.angleShiftR # Adjust target angle by the angle shift
        targetAngleL = self.angleShiftL - targetAngle # Adjust target angle by the angle shift

        pulse_widthR = int(500 + (targetAngleR / 180.0) * 2000)  # Map 0-180 degrees to 500-2500us
        pulse_widthL = int(500 + (targetAngleL / 180.0) * 2000)  # Map 0-180 degrees to 500-2500us
        if (pulse_widthR < 2500 and pulse_widthR > 500) and (pulse_widthL < 2500 and pulse_widthR > 500):
            self.servoR.set_servo_pulsewidth(self.servoPinR, pulse_widthR)
            self.servoL.set_servo_pulsewidth(self.servoPinL, pulse_widthL)
        else:
            print("Error: Pulse width out of bounds")    

    def getMinAngle(self):
        return self.minAngle    
    
    def getMaxAngle(self):
        return self.maxAngle
       
    def stop(self):
        self.servoR.set_servo_pulsewidth(self.servoPinR, 0)
        self.servoL.set_servo_pulsewidth(self.servoPinL, 0)