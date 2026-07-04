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

class Hydro:
    def __init__(self, station_number):
        self.station_number = station_number
        self.GPIO = GPIO
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.on_off_switch = Button(23)           # power the pump on or off
        self.water_level_low_switch = Button(16)  # water level sensor switch
        self.turbine = MCP3008(0)                 # turbine that generates electricity from a motor - is read via an analogue input (MCP3008 ADC chip)
        self.pump_pin = 26                        # pin used to turn on the pump
        GPIO.setup(self.pump_pin, GPIO.OUT)   
        self.power_led = LED(24)                  # the power LED indicator (green)
        self.water_level_led = LED(12)            # the water level LED indicator (red)
        self.display = segments.Seg7x4(self.i2c)
        
        # MQTT message settings
        # Topic is hydro/n where n is the station number
        self.MQTT_BROKER = "hydrobroker.local"
        self.MQTT_TOPIC = f"hydro/{station_number}"

    def __del__(self):
        self.pump_off()
        GPIO.cleanup()

    def get_energy(self):
        """Compute energy as a permille (out of 1000) of the analogue input"""
        return round(self.turbine.value * 1000)
    

    def send_energy(self, energy):
        """Send energy to the village via MQTT"""
        try:
            publish.single(self.MQTT_TOPIC, energy, hostname=self.MQTT_BROKER) #, qos=0, retain=False, keepalive=1)
        except Exception as e:
            print(e)

    def pump_on(self):
        """Turn the pump on"""
        GPIO.output(self.pump_pin, GPIO.HIGH)
        print("Pumping")

    def pump_off(self):
        """Turn the pump off"""
        GPIO.output(self.pump_pin, GPIO.LOW)
        print("Not pumping")

    def show(self, message):
        """Display a message on the 7-segment display"""
        self.display.fill("")
        self.display.print(message)