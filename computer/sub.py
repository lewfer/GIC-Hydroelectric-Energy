import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected successfully.")
    client.subscribe("anonymous/chat")

def on_message(client, userdata, msg):
    print(f"New message: {msg.payload.decode()}")

# Initialize client using MQTTv5
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker (localhost if running on the same machine)
#client.connect("localhost", 1883, 60)
client.connect("192.168.178.11", 1883, 60)

print("Waiting for messages... Press Ctrl+C to exit.")
client.loop_forever()