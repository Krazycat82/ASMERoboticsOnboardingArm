import time
import math
import random
from SingleServoJoint import SingleServoJoint
from DoubleServoJoint import DoubleServoJoint

class FullArmControl:
    shoulderYaw = None
    shoulderPitch = None
    forearm = None
    wrist = None
    grabber = None

    upperArmLength = 0.0
    forearmLength = 0.0

    shoulderYawAngle = 0.0
    shoulderPitchAngle = 0.0
    forearmAngle = 0.0
    wristAngle = 0.0

    def __init__(self, shoulderYawPin, shoulderPitchPinL, shoulderPitchPinR, forearmPin, wristPin, grabberPin):
        self.shoulderYaw = SingleServoJoint(shoulderYawPin, -90, 90, 90)
        self.shoulderPitch = DoubleServoJoint(shoulderPitchPinL, shoulderPitchPinR, 0, 180, 180, 0)
        self.forearm = SingleServoJoint(forearmPin, -90, 90, 0)
        self.wrist = SingleServoJoint(wristPin, -90, 90, 0)
        self.grabber = SingleServoJoint(grabberPin, 0, 90, 0)

    def zero(self):
        self.shoulderYaw.zero()
        self.shoulderPitch.zero()
        self.forearm.zero()
        self.wrist.zero()
        self.grabber.zero()
        print("Moving to zero position")
        time.sleep(2)
        self.stop()

    def stop(self):
        self.shoulderYaw.stop()
        self.shoulderPitch.stop()
        self.forearm.stop()
        self.wrist.stop()
        self.grabber.stop()
        print("Stopped all servos")

    def calcAngles(self, radius, height):
        # Calculate the angles for the shoulder and forearm servos based on x and y coordinates
        hypotenuse = math.sqrt(radius**2 + height**2)
        if hypotenuse > self.upperArmLength + self.forearmLength:
            raise ValueError("Target position is out of reach")
        
        self.forearmInnerAngle = math.acos((self.upperArmLength**2 + self.forearmLength**2 - hypotenuse**2) / (2 * self.upperArmLength * self.forearmLength))
        self.forearmAngle =  math.degrees(self.forearmInnerAngle) - 180

        self.shoulderPitchAngle = math.asin((self.forearmLength / hypotenuse) * math.sin(math.radians(self.forearmAngle))) + math.asin(height / hypotenuse) 
        self.shoulderPitchAngle = math.degrees(self.shoulderPitchAngle)

        self.wristAngle = 0 - self.forearmAngle - self.shoulderPitchAngle

    def moveToPosition(self, x, y, z):
        # Calculate the radius and height from the target position
        radius = math.sqrt(x**2 + y**2)
        height = z

        # Calculate the angles for the shoulder and forearm servos
        self.calcAngles(radius, height)

        # Move the servos to the calculated angles
        self.shoulderYaw.move_to_angle(math.degrees(math.atan2(y, x)))
        self.shoulderPitch.move_to_angle(self.shoulderPitchAngle)
        self.forearm.move_to_angle(self.forearmAngle)
        self.wrist.move_to_angle(self.wristAngle)

    def demo():

        while True:

            x = random.random() * (self.upperArmLength + self.forearmLength) 
            y = random.random() * (self.upperArmLength + self.forearmLength)
            z = random.random() * (self.upperArmLength + self.forearmLength)
            print(f"Moving to position: x={x}, y={y}, z={z}")

            try:
                self.moveToPosition(x, y, z)
                time.sleep(2)  # Allow time for the arm to move
            except ValueError as e:
                print(f"Error: {e}. Position out of reach. Retrying...")
                continue