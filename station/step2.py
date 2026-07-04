# Step 2: Check water level

from hydro_lib import *

hydro = Hydro(1)

print("Ready...")

while True:
    # Check if we have enough water in the reservoir
    water_level_ok = not hydro.water_level_low_switch.is_pressed
    if water_level_ok:
        hydro.water_level_led.off()
    else:
        hydro.water_level_led.on()

    if hydro.on_off_switch.is_pressed:
        # Power switch is on
        hydro.power_led.on()
        hydro.show("ON")
    else:
        # Power switch is off
        hydro.power_led.off()
        hydro.show("OFF")

    sleep(0.5)
