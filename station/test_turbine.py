from gpiozero import MCP3008
from time import sleep

turbine = MCP3008(0)

while True:
    print(round(turbine.value,2))
    sleep(0.1)
