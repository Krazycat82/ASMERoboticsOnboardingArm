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
        self.forearm = SingleServoJoint(forearmPin, -90, 110, 90)
        self.wrist = SingleServoJoint(wristPin, -90, 90, 90)
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
        #self.stop()

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
        if hypotenuse > self.upperArmLength + self.forearmLength + 0.1:  # Adding a small tolerance to avoid floating point issues
            # If the target position is out of reach, raise an error:
           # print(f"Target position: radius={radius}, height={height}, hypotenuse={hypotenuse}, length={self.upperArmLength + self.forearmLength}")
            raise ValueError("Target position is out of reach, desired reach is too far.")
        
        #print(f"Value: {2 * self.upperArmLength * self.forearmLength}")
        #print(f"FIA Equation piece: {self.upperArmLength**2 + self.forearmLength**2 - hypotenuse**2} / {2 * self.upperArmLength * self.forearmLength}")
        if abs((self.upperArmLength**2 + self.forearmLength**2 - hypotenuse**2) / (2 * self.upperArmLength * self.forearmLength)) < 1.0:
            self.forearmInnerAngle = math.acos((self.upperArmLength**2 + self.forearmLength**2 - hypotenuse**2) / (2 * self.upperArmLength * self.forearmLength))
        elif abs((self.upperArmLength**2 + self.forearmLength**2 - hypotenuse**2) / (2 * self.upperArmLength * self.forearmLength)) < 1.001:
            self.forearmInnerAngle = math.acos(-1.0)
        self.forearmAngle =  180 - math.degrees(self.forearmInnerAngle)

        #print(f"Calculated forearm inner angle: {math.degrees(self.forearmInnerAngle)} degrees")

        self.shoulderPitchAngle = math.asin((self.forearmLength / hypotenuse) * math.sin(self.forearmInnerAngle)) + math.asin(height / hypotenuse) 
        self.shoulderPitchAngle = math.degrees(self.shoulderPitchAngle)

        self.wristAngle = self.forearmAngle - self.shoulderPitchAngle
        print(f"Calculated angles: shoulderPitch={self.shoulderPitchAngle}, forearm={self.forearmAngle}, wrist={self.wristAngle}")

    def moveToPosition(self, x, y, z):
        # Calculate the radius and height from the target position
        print("Entered moveToPosition")
        radius = math.sqrt(x**2 + y**2)
        print("calced radius")
        height = z
        print(f"Moving to position: x={x}, y={y}, z={z}, radius={radius}, height={height}")


        # Calculate the angles for the shoulder and forearm servos
        self.calcAngles(radius, height)

        # Move the servos to the calculated angles
        if self.shoulderPitchAngle > self.shoulderPitch.getMinAngle() and self.shoulderPitchAngle < self.shoulderPitch.getMaxAngle() and self.shoulderYawAngle > self.shoulderYaw.getMinAngle() and self.shoulderYawAngle < self.shoulderYaw.getMaxAngle() and self.forearmAngle > self.forearm.getMinAngle() and self.forearmAngle < self.forearm.getMaxAngle() and self.wristAngle > self.wrist.getMinAngle() and self.wristAngle < self.wrist.getMaxAngle():
            self.shoulderYaw.move_to_angle(math.degrees(math.atan2(x, y)))
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

        self.stop()

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

        print("Key control mode. Use R/F for Z, A/D for angle, W/S for radius, Q to quit.")

        # Initial position
        state = {'x': 0.0, 'y': 400.0, 'z': 0.0, 'grabbing': False, 'running': True}
        step = 20.0  # mm per key press
        angle_step = math.radians(5)  # radians per a/d

        def press(key):
            print(f"\nKey pressed: {key}")
            if not state['running']:
                return
            x, y, z = state['x'], state['y'], state['z']
            print(f"Original position: x={state['x']:.1f}, y={state['y']:.1f}, z={state['z']:.1f}")
            angle = math.atan2(x, y)  # Current angle in radians
            radius = math.hypot(x, y)
            print(f"Original radius: {radius:.1f} mm, Angle: {math.degrees(angle):.1f}°, Height (z): {z:.1f} mm\n")

            if key == 'r':
                z += step
            elif key == 'f':
                z -= step
            elif key == 'a':
                angle = angle + angle_step
            elif key == 'd':
                angle = angle - angle_step
            elif key == 'w':
                radius = radius + step
            elif key == 's':
                radius = max(0, radius - step)
            elif key == 'q':
                print("Exiting key control.")
                state['running'] = False
                self.stop()
                return
            elif key == 'space':
                if state['grabbing'] == True:
                    self.grabber.move_to_angle(self.grabber.getMaxAngle())
                    state['grabbing'] = False
                else:
                    self.grabber.move_to_angle(self.grabber.getMinAngle())
                    state['grabbing'] = True

                print("Grabbing: ", state['grabbing'])
            else:
                return
            
            x = radius * math.sin(angle)
            y = radius * math.cos(angle)

            state['x'], state['y'], state['z'] = x, y, z
            print(f"Changed position: x={state['x']:.1f}, y={state['y']:.1f}, z={state['z']:.1f}")

            radius = math.hypot(x, y)
            angle = math.degrees(math.atan2(x, y))
            print(f"Changed radius: {radius:.1f} mm, Angle: {angle:.1f}°, Height (z): {z:.1f} mm\n")

            try:
                self.moveToPosition(x, y, z)
            except ValueError as e:
                print(f"Error: {e}")


        print(f"Current position: x={state['x']:.1f}, y={state['y']:.1f}, z={state['z']:.1f}")
        listen_keyboard(on_press=press, until="q")

        self.stop()