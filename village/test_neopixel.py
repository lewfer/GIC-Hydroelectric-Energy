from time import sleep
from board import D18
from neopixel import NeoPixel

# Choose the pin you connected the data line to (GPIO 18 is Pin 12)
pixel_pin = D18

# Number of NeoPixels you are using
num_pixels = 30

pixels = NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)

# Turn red
for i in range(num_pixels):
    pixels[i] = (255, 0, 0)
pixels.show()
sleep(5)

# Turn this colour
for i in range(num_pixels):
    pixels[i] = (127, 66, 200)
pixels.show()
sleep(5)

# Turn them all off
pixels.fill((0, 0, 0))
pixels.show()