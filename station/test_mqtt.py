import paho.mqtt.publish as publish
 
MQTT_SERVER = "192.168.178.11"
MQTT_TOPIC = "hydro/0"
 
publish.single(MQTT_TOPIC, 33, hostname=MQTT_SERVER)
