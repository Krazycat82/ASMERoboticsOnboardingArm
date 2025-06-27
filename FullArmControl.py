import time
import math
import random
from SingleServoJoint import SingleServoJoint
from DoubleServoJoint import DoubleServoJoint
from sshkeyboard import listen_keyboard

class FullArmControl:
    shoulderYaw = None
    shoulderPitch = None
    forearm = None
    wrist = None
    grabber = None

    upperArmLength = 200 # mm
    forearmLength = 200 # mm

    shoulderYawAngle = 0.0
    shoulderPitchAngle = 0.0
    forearmAngle = 0.0
    wristAngle = 0.0

    def __init__(self, shoulderYawPin, shoulderPitchPinL, shoulderPitchPinR, forearmPin, wristPin, grabberPin):
        self.shoulderYaw = SingleServoJoint(shoulderYawPin, -90, 90, 90)
        self.shoulderPitch = DoubleServoJoint(shoulderPitchPinL, shoulderPitchPinR, 0, 180, 180, 0)
        self.forearm = SingleServoJoint(forearmPin, -90, 90, 110)
        self.wrist = SingleServoJoint(wristPin, -90, 90, 110)
        self.grabber = SingleServoJoint(grabberPin, 0, 90, 30)

    def zero(self):
        zeroSleepTime = 1.5

        self.shoulderYaw.zero()
        print("Moving shoulderYaw to zero position")
        time.sleep(zeroSleepTime)

        self.grabber.zero()
        print("Moving grabber to zero position")
        time.sleep(zeroSleepTime)

        self.wrist.zero()
        print("Moving wrist to zero position")
        time.sleep(zeroSleepTime)

        self.forearm.zero()
        print("Moving forearm to zero position")
        time.sleep(zeroSleepTime)

        self.shoulderPitch.zero()
        print("Moving shoulderPitch to zero position")
        time.sleep(zeroSleepTime)        

        print("All servos moved to zero position")
        #input("Press Enter to stop the servos...")
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
        
        #print(f"Value: {2 * self.upperArmLength * self.forearmLength}")
        
        self.forearmInnerAngle = math.acos((self.upperArmLength**2 + self.forearmLength**2 - hypotenuse**2) / (2 * self.upperArmLength * self.forearmLength))
        self.forearmAngle =  math.degrees(self.forearmInnerAngle)

        self.shoulderPitchAngle = math.asin((self.forearmLength / hypotenuse) * math.sin(math.radians(self.forearmAngle))) + math.asin(height / hypotenuse) 
        self.shoulderPitchAngle = math.degrees(self.shoulderPitchAngle)

        self.wristAngle = self.forearmAngle - self.shoulderPitchAngle
        print(f"Calculated angles: shoulderPitch={self.shoulderPitchAngle}, forearm={self.forearmAngle}, wrist={self.wristAngle}")

    def moveToPosition(self, x, y, z):
        # Calculate the radius and height from the target position
        radius = math.sqrt(x**2 + y**2)
        height = z

        # Calculate the angles for the shoulder and forearm servos
        self.calcAngles(radius, height)

        # Move the servos to the calculated angles
        if self.shoulderPitchAngle > self.shoulderPitch.getMinAngle() and self.shoulderPitchAngle < self.shoulderPitch.getMaxAngle() and self.shoulderYawAngle > self.shoulderYaw.getMinAngle() and self.shoulderYawAngle < self.shoulderYaw.getMaxAngle() and self.forearmAngle > self.forearm.getMinAngle() and self.forearmAngle < self.forearm.getMaxAngle() and self.wristAngle > self.wrist.getMinAngle() and self.wristAngle < self.wrist.getMaxAngle():
            self.shoulderYaw.move_to_angle(math.degrees(math.atan2(y, x)))
            self.shoulderPitch.move_to_angle(self.shoulderPitchAngle)
            self.forearm.move_to_angle(self.forearmAngle)
            self.wrist.move_to_angle(self.wristAngle)
        elif self.shoulderPitchAngle < self.shoulderPitch.getMinAngle() or self.shoulderPitchAngle > self.shoulderPitch.getMaxAngle():
            raise ValueError("Calculated shoulder pitch is out of bounds")
        elif self.shoulderYawAngle < self.shoulderYaw.getMinAngle() or self.shoulderYawAngle > self.shoulderYaw.getMaxAngle():
            raise ValueError("Calculated shoulder yaw is out of bounds")
        elif self.forearmAngle < self.forearm.getMinAngle() or self.forearmAngle > self.forearm.getMaxAngle():
            raise ValueError("Calculated forearm angle is out of bounds")
        elif self.wristAngle < self.wrist.getMinAngle() or self.wristAngle > self.wrist.getMaxAngle():
            raise ValueError("Calculated wrist angle is out of bounds")
        

    def demo(self):

        while input("\nPress Enter to move the arm to a random position (or type 'exit' to quit): ") != 'exit':

            x = random.random() * (self.upperArmLength + self.forearmLength) * (1 if random.random() > 0.5 else -1)
            y = random.random() * math.sqrt((self.upperArmLength + self.forearmLength)**2 - x**2)
            z = random.random() * math.sqrt((self.upperArmLength + self.forearmLength)**2 - x**2 - y**2)
            print(f"Moving to position: x={x}, y={y}, z={z}")

            try:
                self.moveToPosition(x, y, z)
                time.sleep(2)  # Allow time for the arm to move
            except ValueError as e:
                print(f"Error: {e}. Position out of reach. Retrying...")
                continue

    def manualControl(self):
        print("Manual XYZ control mode. Type 'exit' to quit.")
        while True:
            try:
                user_input = input("Enter target x y z (space-separated): ")
                if user_input.strip().lower() == 'exit':
                    break
                x_str, y_str, z_str = user_input.strip().split()
                x = float(x_str)
                y = float(y_str)
                z = float(z_str)
                self.moveToPosition(x, y, z)
                print(f"Moved to position: x={x}, y={y}, z={z}")
            except ValueError as e:
                print(f"Invalid input or error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    def keyControl(self):
        """
        Control the arm using keys:
        - R/F: Increase/decrease Z (height)
        - A/D: Move X/Y in a circular direction
        - W/S: Increase/decrease radius (distance from base)
        - Q: Quit
        """
        #try:
        #except ImportError:
        #    print("The 'sshkeyboard' module is required for key control. Install it with 'pip install sshkeyboard'.")
        #    return

        print("Key control mode. Use R/F for Z, A/D for angle, W/S for radius, Q to quit.")

        # Initial position
        state = {'x': 0.0, 'y': 100.0, 'z': 0.0, 'running': True}
        step = 10.0  # mm per key press
        angle_step = math.radians(5)  # radians per a/d

        def press(key):
            if not state['running']:
                return
            x, y, z = state['x'], state['y'], state['z']
            if key == 'r':
                z += step
            elif key == 'f':
                z -= step
            elif key == 'a':
                angle = math.atan2(y, x) + angle_step
                radius = math.hypot(x, y)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
            elif key == 'd':
                angle = math.atan2(y, x) - angle_step
                radius = math.hypot(x, y)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
            elif key == 'w':
                radius = math.hypot(x, y) + step
                angle = math.atan2(y, x)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
            elif key == 's':
                radius = max(0, math.hypot(x, y) - step)
                angle = math.atan2(y, x)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
            elif key == 'q':
                print("Exiting key control.")
                state['running'] = False
                return
            else:
                return

            state['x'], state['y'], state['z'] = x, y, z
            print(f"Current position: x={x:.1f}, y={y:.1f}, z={z:.1f}")
            try:
                self.moveToPosition(x, y, z)
            except ValueError as e:
                print(f"Error: {e}")

        print(f"Current position: x={state['x']:.1f}, y={state['y']:.1f}, z={state['z']:.1f}")
        listen_keyboard(on_press=press, until="q")