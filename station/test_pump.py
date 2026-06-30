
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pump_pin = 26                        # pin used to turn on the pump
GPIO.setup(pump_pin, GPIO.OUT) 

# Note: this motor cannot run in reverse or vary speed using PWM

GPIO.output(pump_pin, GPIO.HIGH) # Turns the pump ON
sleep(2)  
GPIO.output(pump_pin, GPIO.LOW)  # Turns the pump OFF


