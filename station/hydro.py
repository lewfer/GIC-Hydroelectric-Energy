# Hydroelectric power station controller
# This code runs on a raspberry pi

# Imports
from gpiozero import Button
from gpiozero import LED
from gpiozero import MCP3008
# from board import D18
# from neopixel import NeoPixel
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.publish as publish

# MQTT message settings
# Topic is hydro/n where n is the station number
MQTT_BROKER = "hydrobroker"
MQTT_TOPIC = "hydro/0"

GPIO.setmode(GPIO.BCM)

# Connected devices
on_off_switch = Button(23)           # power the pump on or off
water_level_low_switch = Button(16)  # water level sensor switch
turbine = MCP3008(0)                 # turbine that generates electricity from a motor - is read via an analogue input (MCP3008 ADC chip)
pump_pin = 21                        # pin used to turn on the pump
GPIO.setup(pump_pin, GPIO.OUT)       
#pixel_pin = D18                      # pin used to power the neopixels
power_led = LED(24)                  # the power LED indicator (green)
water_level_led = LED(20)            # the water level LED indicator (red)

# Number of NeoPixels you are using
# num_pixels = 30
# pixels = NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)

print("Ready...")
try:
    while True:
        # Check if we have enough water in the reservoir
        water_level_ok = not water_level_low_switch.is_pressed
        if water_level_ok:
            water_level_led.off()
        else:
            water_level_led.on()

        # 
        if on_off_switch.is_pressed:
            power_led.on()
            energy = round(turbine.value*100)
            if water_level_ok:
                print("Pumping", energy)
                GPIO.output(pump_pin, GPIO.HIGH) # Turns the pump ON


                publish.single(MQTT_TOPIC, energy, hostname=MQTT_BROKER)                
            else: 
                print("Not pumping", energy)
                GPIO.output(pump_pin, GPIO.LOW)  # Turns the pump OFF

            # Light up neopixels accoriding to energy levels
            # for i in range(energy):
            #     pixels[i] = (255, 0, 0)
            # for i in range(num_pixels-1, energy-1, -1):
            #     pixels[i] = (0, 0, 0)                
            # pixels.show()

        else:
            power_led.off()
            print("Pump power off")
            GPIO.output(pump_pin, GPIO.LOW) # Turns the pump OFF
        sleep(0.5)

except KeyboardInterrupt:
    pass
finally:
    GPIO.output(pump_pin, GPIO.LOW)
    # pixels.fill((0, 0, 0))
    # pixels.show()
    GPIO.cleanup()



