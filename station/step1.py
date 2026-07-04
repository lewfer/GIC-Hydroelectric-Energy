# Step 1: Operate the on/off switch

from hydro_lib import *

hydro = Hydro(1)

print("Ready...")

while True:
    if hydro.on_off_switch.is_pressed:
        # Power switch is on
        hydro.power_led.on()
        hydro.show("ON")
    else:
        # Power switch is off
        hydro.power_led.off()
        hydro.show("OFF")

    sleep(0.5)
