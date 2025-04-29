import time

import RPi.GPIO as GPIO

# Pin configuration
servo_pin = 14  # Replace with the GPIO pin connected to your servo

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Set up PWM for the servo
pwm = GPIO.PWM(servo_pin, 50)  # 50Hz frequency
pwm.start(0)

try:
    # Rotate servo to 0 degrees
    duty_cycle = 2.5  # Adjust this value if needed for your servo
    pwm.ChangeDutyCycle(duty_cycle)
    print("Starting")
    time.sleep(1)  # Allow time for the servo to move
    print("Ending")
finally:
    # Cleanup
    #pwm.ChangeDutyCycle(0)
    pwm.stop()