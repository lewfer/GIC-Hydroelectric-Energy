# Hydroelectric power station controller
# This code runs on a raspberry pi

# Imports
from gpiozero import Button
from gpiozero import LED
from gpiozero import MCP3008
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.publish as publish
import board
import busio
from adafruit_ht16k33 import segments

# MQTT message settings
# Topic is hydro/n where n is the station number
MQTT_BROKER = "hydrobroker"
MQTT_TOPIC = "hydro/1"

GPIO.setmode(GPIO.BCM)

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Connected devices
on_off_switch = Button(23)           # power the pump on or off
water_level_low_switch = Button(16)  # water level sensor switch
turbine = MCP3008(0)                 # turbine that generates electricity from a motor - is read via an analogue input (MCP3008 ADC chip)
pump_pin = 26                        # pin used to turn on the pump
GPIO.setup(pump_pin, GPIO.OUT)   
power_led = LED(24)                  # the power LED indicator (green)
water_level_led = LED(12)            # the water level LED indicator (red)
display = segments.Seg7x4(i2c)

display.print(42)

print("Ready...")
try:
    while True:
        # Check if we have enough water in the reservoir
        water_level_ok = not water_level_low_switch.is_pressed
        if water_level_ok:
            water_level_led.off()
        else:
            water_level_led.on()

        # Pump water and read energy
        if on_off_switch.is_pressed:
            power_led.on()
            energy = round(turbine.value*1000) # compute energy as a permille (out of 1000) of the analogue input
            if water_level_ok:
                # Turn ump on and send the energy to the village
                print("Pumping", energy)
                GPIO.output(pump_pin, GPIO.HIGH) # Turns the pump ON
                
                display.fill("")
                display.print(energy)
                try:
                    publish.single(MQTT_TOPIC, energy, hostname=MQTT_BROKER)
                except Exception as e:
                    print(e)            
            else: 
                # Turn pump off
                print("Not pumping", energy)
                GPIO.output(pump_pin, GPIO.LOW)  # Turns the pump OFF
        else:
            power_led.off()
            print("Pump power off")
            GPIO.output(pump_pin, GPIO.LOW) # Turns the pump OFF
        sleep(0.5)

except KeyboardInterrupt:
    pass
finally:
    GPIO.output(pump_pin, GPIO.LOW)
    GPIO.cleanup()



