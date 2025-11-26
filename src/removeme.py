from myMqttClient import MQTTclient

mqtt_client = MQTTclient()
def cb(msg):
    print("Received message:", msg.payload.decode())
print("Starting MQTT client loop")
mqtt_client.loop_start()
print("Subscribing to test/topic")
mqtt_client.subscribe("test/topic")
print("Publishing message to test/topic")
mqtt_client.publish("test/topic", "Hello, MQTT!")
while True:
    pass