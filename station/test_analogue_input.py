from gpiozero import MCP3008
from time import sleep

pot = MCP3008(0)

while True:
    print(round(pot.value,2))
    sleep(0.1)
