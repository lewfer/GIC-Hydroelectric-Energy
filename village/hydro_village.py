import paho.mqtt.client as mqtt
from board import D18
from neopixel import NeoPixel
from time import sleep
import random
from decimal import Decimal

import board
import busio
from adafruit_ht16k33 import segments

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the LED segment class.
# This creates a 7 segment 4 character display:
display = segments.Seg7x4(i2c)

# Clear the display.
display.fill(0)

MQTT_SERVER = "hydrobroker" # Change to name of your publisher 
MQTT_TOPIC = "hydro/+"

pixel_pin = D18

# Number of NeoPixels you are using
num_pixels = 50
pixels = NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)

num_stations = 6
num_stations_incl_battery = num_stations + 1

# Colour of each station (colours from https://colorbrewer2.org/#type=qualitative&scheme=Set1&n=7))
colours = [(166,86,40), (228,26,28), (55,126,184), (77,175,74), (152,78,163), (255,127,0), (255,255,51)]

# How much each station has generated
# Station 0 is the battery
generated = [0] * num_stations_incl_battery

# Compute the expected energy generation so we can scale the generated energy to the number of pixels
# This should be the amount of energy to light up all the houses
# Any energy above this will go to the battery
expected_energy_per_station = 30    # max is 100
total_needed_energy = expected_energy_per_station * num_stations
print("total_needed_energy", total_needed_energy)


# Assigned station of each pixel
allocations = [-1] * num_pixels

#energy = 0
battery_level = 0



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic, int(msg.payload))
    # more callbacks, etc

    # Strip the topic to get the station name
    station_number = int(msg.topic.split("/")[1])

    # Get the energy value from the message payload
    energy = int(msg.payload)
    print(energy)

    # Update the generated energy for the station 
    generated[station_number] = energy 

# Rebalance array of generated energy to num_pixels
# demand_satisfaction of 1 means 100% of pixels will be on
def rebalance(generated, demand_satisfaction):
    # Copy the generation array to avoid modifying it while iterating
    generated_copy = generated.copy()

    total_energy = sum(generated_copy)
    print("Available energy:", generated_copy, "=", total_energy)
    print("Demand satisfaction", round(demand_satisfaction*100, 2))
    if demand_satisfaction>0:
        scale = Decimal(total_energy)/Decimal(num_pixels)/Decimal(demand_satisfaction)
        print("scale", scale)
        rounding_error = 0
        for i in range(len(generated_copy)):
            div = Decimal(generated_copy[i]) / scale
            generated_copy[i] = int(round(div))
            rounding_error += generated_copy[i] - div
            #print(rounding_error)
            if round(rounding_error,1)>=1:
                #print("rounding_error", rounding_error)
                rounding_error -= 1
                generated_copy[i] -=1
            elif round(rounding_error,1)<=-1:
                print("rounding_error", rounding_error)
                rounding_error += 1
                generated_copy[i] +=1                
        new_total_energy = sum(generated_copy)
        print("Rebalanced energy", total_energy, "by scaling by", round(scale,4), "to", new_total_energy, generated_copy)
    return generated_copy


def randomize_pixels():
    n = [i for i in range(num_pixels)]
    random.shuffle(n)
    return n

def reduce_station_energy():
    # Reduce the energy of each station by 1, to simulate energy being used
    for i in range(1, num_stations_incl_battery):
        generated[i] -= 10
        if generated[i]<0:
            generated[i] = 0
        #print("Reducing energy of station", i, "to", generated[i])
            
# Main
# -------------------------------------------------------

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(MQTT_SERVER, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()

# Turn off all pixels at the start
for i in range(num_pixels):
    pixels[i] = 0
pixels.show()
sleep(1)

# Start the background thread
client.loop_start()

# Main thread is free to do other work
try:
    while True:
        print("\nLoop...")

        # Reset any existing battery power from previous loop
        generated[0] = 0

        print("New energy generated:", generated)

        # Compute how much new energy we have from the stations 
        new_energy = sum(generated)

        # Excess energy goes to the battery and remaining new energy is used to turn on houses
        for_battery = max(new_energy - total_needed_energy, 0)
        utilisable_energy = min(new_energy, total_needed_energy)
        print("New energy generated:", new_energy, "Utilisable energy:", utilisable_energy)
        battery_level += for_battery
        print("Energy to battery:", for_battery, "Battery level:", battery_level)

        display.fill("")
        display.print(battery_level)

        # If we need battery backup, add it to generated
        if battery_level>0:
            print("Using battery backup")
            # Use battery to make up the difference between total_needed_energy and utilisable_energy
            battery_used = min(battery_level, total_needed_energy - utilisable_energy)
            print("Battery used:", battery_used)
            battery_level -= battery_used
            utilisable_energy += battery_used
            print("New utilisable energy:", utilisable_energy, "Battery level:", battery_level)
            generated[0] = battery_used
           
        # Rescale generated to number of pixels, so generated_scaled will be the number of pixels to turn on for each station
        generated_scaled = rebalance(generated, utilisable_energy/total_needed_energy)

        # Randomly order the pixels, so we can turn on/off pixels in a random order
        random_pixels = randomize_pixels()

        # Find how many of each station/colour to turn on/off
        # Store this in the change[] array
        count_on = [0] * num_stations_incl_battery
        for station in allocations:
            if station!= -1: # Pixel is already on
                count_on[station] += 1
        print("Count pixels on by station:", count_on)
        change = [0] * num_stations_incl_battery
        for i in range(num_stations_incl_battery):
            change[i] = generated_scaled[i] - count_on[i]
        print("Change in pixel count by station:", change)

        # Find pixels to turn off
        # Work through the change[] array and for each station, if change is negative, turn off that many pixels of that station
        for station, change_count in enumerate(change):
            p = iter(random_pixels)
            while change_count<0: #for i in range(-change_count):
                pix = next(p)
                if allocations[pix] == station:
                    allocations[pix] = -1
                    #print("Turning off pixel", pix, "for station", station)
                    pixels[pix] = 0
                    change_count += 1

        # Find pixels to turn on
        # Work through the change[] array and for each station, if change is positive, turn on that many pixels of that station
        for station, change_count in enumerate(change):
            p = iter(random_pixels)
            while change_count>0:
                pix = next(p)
                if allocations[pix] == -1:
                    allocations[pix] = station
                    #print("Turning on pixel", pix, "for station", station)
                    pixels[pix] = colours[station]
                    change_count -= 1

        
        # print(allocations)
        # print(pixels)
        pixels.show()

        reduce_station_energy()

        sleep(1) #!!
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Always clean up background threads and connections
    client.loop_stop()
    client.disconnect()