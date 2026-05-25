import paho.mqtt.client as mqtt
from board import D18
from neopixel import NeoPixel

MQTT_SERVER = "hydrobroker" # Change to name of your publisher 
MQTT_TOPIC = "hydro/+"

pixel_pin = D18

# Number of NeoPixels you are using
num_pixels = 30
pixels = NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)


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

    energy = int(msg.payload)
    print(energy)
    for i in range(energy):
        pixels[i] = (255, 0, 0)
    for i in range(num_pixels-1, energy-1, -1):
        pixels[i] = (0, 0, 0)                
    pixels.show()
 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(MQTT_SERVER, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
