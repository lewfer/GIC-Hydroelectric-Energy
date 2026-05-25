import RPi.GPIO as GPIO
import time

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)
pin = 21
GPIO.setup(pin, GPIO.OUT)

try:
    while True:
        print("on")
        GPIO.output(pin, GPIO.HIGH) # Turns the transistor/load ON
        time.sleep(3)
        print("off")
        GPIO.output(pin, GPIO.LOW)  # Turns the transistor/load OFF
        time.sleep(3)

except KeyboardInterrupt:
    GPIO.cleanup()