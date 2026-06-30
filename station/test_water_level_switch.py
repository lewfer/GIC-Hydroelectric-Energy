from gpiozero import Button
from time import sleep

on_off_switch = Button(16)

while True:
    print(on_off_switch.is_pressed)
    sleep(0.2)
