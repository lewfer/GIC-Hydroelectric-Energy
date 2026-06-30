from gpiozero import LED
from time import sleep

power_led = LED(24)                  # the power LED indicator (green)
water_level_led = LED(12)            # the water level LED indicator (red)

power_led.on()
water_level_led.on()
sleep(2)
power_led.off()
water_level_led.off()