from time import sleep
from board import D18
from neopixel import NeoPixel
import random
from decimal import Decimal

# Choose the pin you connected the data line to (GPIO 18 is Pin 12)
pixel_pin = D18

# Number of NeoPixels you are using
num_pixels = 50

num_stations = 4

# Colour of each station
colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]

# How much each station has generated
generation = [0] * num_pixels

energy = 0
battery = 0

# Assigned station of each pixel
allocations = [-1] * num_pixels
print(allocations)

pixels = NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)

def turnOn(num_pixels):
    count = 0
    while count < num_pixels:
        try_pixel = random.randint(0, num_pixels-1)
        print("try_pixel", try_pixel)
        if allocations[try_pixel] == 0:
            allocations[try_pixel] = (255, 0, 0) #!!
            count += 1

def turnOff(num_pixels):
    count = 0
    while count < num_pixels:
        try_pixel = random.randint(0, num_pixels-1)
        print("try_pixel", try_pixel)
        if allocations[try_pixel] != 0:
            allocations[try_pixel] = 0
            count += 1

def find_station_with_energy(start_station, generation):
    station = start_station

    # Search to end of array
    while station < num_stations:
        if generation[station] > 0:
            return station
        station += 1

    # Search from start
    while station < start_station:
        if generation[station] > 0:
            return station
        station += 1 

    # No energy found
    return -1

def randomize_pixels():
    n = [i for i in range(num_pixels)]
    random.shuffle(n)
    return n

# Turn on the requested number of pixels, spreading colours evenly based on generation from each station
def turnOnPerStation(num_pixels, generation):
    station = random.randint(0, num_stations-1)
    
    a = randomize_pixels()
    count = 0
    p = 0
    while count < num_pixels:
        try_pixel = a[p]
        print("try_pixel", try_pixel)
        sleep(1)
        if allocations[try_pixel] == 0:
            print("FOund empty pixel")
            # Find a station that still has energy and use that station's colour
            station = find_station_with_energy(station, generation)
            print("station", station)
            if station == -1:
                break # no station with energy
            allocations[try_pixel] = colours[station]
            generation[station] -= 1
            print(generation)
            station += 1
            count += 1
        p += 1
    print("Done")

def turnOffPerStation(num_pixels, generation):

    station = random.randint(0, num_stations-1)
    
    a = randomize_pixels()
    count = 0
    p = 0
    while count < num_pixels:
        try_pixel = a[p]
        print("try_pixel", try_pixel)
        sleep(1)
        if allocations[try_pixel] == 0:
            print("FOund empty pixel")
            # Find a station that still has energy and use that station's colour
            station = find_station_with_energy(station, generation)
            print("station", station)
            if station == -1:
                break # no station with energy
            allocations[try_pixel] = colours[station]
            generation[station] -= 1
            print(generation)
            station += 1
            count += 1
        p += 1
    print("Done")

# Rescale generation to num_pixels
def rescale(generation):
    total_energy = sum(generation)
    scale = Decimal(total_energy)/Decimal(num_pixels)
    if scale>1:
        rounding_error = 0
        for i in range(len(generation)):
            div = Decimal(generation[i]) / scale
            generation[i] = round(div)
            rounding_error += generation[i] - div
            print(rounding_error)
            if round(rounding_error,1)>=1:
                print("rounding_error", rounding_error)
                rounding_error -= 1
                generation[i] -=1
            elif round(rounding_error,1)<=-1:
                print("rounding_error", rounding_error)
                rounding_error += 1
                generation[i] +=1                
    new_total_energy = sum(generation)
    print("rebalance", total_energy, "scale", scale, "to", new_total_energy, generation)

for i in range(num_pixels):
    pixels[i] = 0
pixels.show()
sleep(1)

while True:
    #new_energy = random.randint(0, num_pixels)
    #print("New energy:", new_energy)

    # Simulate get energy from stations
    generation =  [random.randint(1, 10) for _ in range(num_stations)] # [7, 6, 6, 6] [10, 7, 9, 4] #[6, 7, 9, 6] #
    print("\nGenerated", generation)

    # Compute how much new energy we have (how many houses to turn on)
    new_energy = sum(generation)

    # Excess energy goes to the battery and remaining new energy is used to turn on houses
    for_battery = max(new_energy - num_pixels, 0)
    new_energy = min(new_energy, num_pixels)
    print("New", new_energy, "For battery", for_battery)

    # Rescale to number of pixels
    rescale(generation)

    # Randomly order the pixels
    random_pixels = randomize_pixels()

    # Find how many of each colour to turn on/off
    count_on = [0] * num_stations
    for station in allocations:
        if station!= -1: # Pixel is already on
            count_on[station] += 1
    print("count_on", count_on)
    change = [0] * num_stations
    for i in range(num_stations):
        change[i] = generation[i] - count_on[i]
    print("change", change)


    # Find pixels to turn off
    for station, change_count in enumerate(change):
        p = iter(random_pixels)
        if change_count<0:
            for i in range(-change_count):
                pix = next(p)
                if allocations[pix] == station:
                    allocations[pix] = -1
                    pixels[pix] = 0

    # Find pixels to turn on
    for station, change_count in enumerate(change):
        p = iter(random_pixels)
        if change_count>0:
            for i in range(change_count):
                pix = next(p)
                if allocations[pix] == -1:
                    allocations[pix] = station
                    pixels[pix] = colours[allocations[pix]]

    pixels.show()

    # # Turn pixels on
    # n = 0
    # p = iter(random_pixels)
    # for station, station_count in enumerate(generation):
    #     for i in range(station_count):
    #         #print(next(p))
    #         pix = next(p)
    #         allocations[pix] = station
    #         pixels[pix] = colours[allocations[pix]]
    # pixels.show()


    """
    if new_energy>energy:
        # Turn on more pixels
        turnOnPerStation(new_energy-energy, generation)
    elif new_energy<energy:
        # Turn off some pixels
        turnOffPerStation(energy-new_energy, generation)

    print(allocations)
    for i in range(num_pixels):
        pixels[i] = allocations[i]
    pixels.show()

    energy = new_energy     
    """

    sleep(1)   
