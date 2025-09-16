import time

# import RPi.GPIO as GPIO
from pigpioFolder import pigpio

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
        self.servoPin = servoPin

        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(servoPin, GPIO.OUT)

        #self.servo = GPIO.PWM(servoPin, 50)  # 50Hz frequency
        #self.servo.start(0)

        self.servo = pigpio.pi()
        self.servo.set_mode(self.servoPin, pigpio.OUTPUT)

    def zero(self):
        self.move_to_angle(0)
        print("Moving to zero position")


    def move_to_angle(self, targetAngle):

        #if targetAngle < self.minAngle or targetAngle > self.maxAngle:
        #    raise ValueError("Target angle is out of bounds")

        targetAngle += self.angleShift # Adjust target angle by the angle shift

        #duty_cycle = 2 + (targetAngle / 18)  # Convert angle to duty cycle
        #print(duty_cycle)
        #self.servo.ChangeDutyCycle(duty_cycle)
        pulse_width = int(500 + (targetAngle / 180.0) * 2000)  # Map 0-180 degrees to 500-2500us

        if (pulse_width < 2500 and pulse_width > 500): 
            #print("pulse_width: ", pulse_width)
            self.servo.set_servo_pulsewidth(self.servoPin, pulse_width)
        else:
            print("Error: Pulse width out of bounds")                


    def getMinAngle(self):
        return self.minAngle
    
    def getMaxAngle(self):
        return self.maxAngle
       
    def stop(self):
        self.servo.set_servo_pulsewidth(self.servoPin, 0)