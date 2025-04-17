import time

import RPi.GPIO as GPIO

# Pin configuration
SERVO_PIN = 18  # GPIO pin connected to the servo

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set up PWM
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frequency
pwm.start(0)

try:
    # Set servo to 0 position
    duty_cycle = 2.5  # 0 degrees corresponds to 2.5% duty cycle
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Allow time for the servo to move
finally:
    # Cleanup
    pwm.stop()
    GPIO.cleanup()