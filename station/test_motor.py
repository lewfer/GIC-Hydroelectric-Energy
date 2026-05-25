from gpiozero import Motor
from time import sleep

# Note: this motor cannot run in reverse or vary speed using PWM

motor1 = Motor(23, 24)
print("Motor 1 forward")
motor1.forward()
sleep(2)  
motor1.stop()


