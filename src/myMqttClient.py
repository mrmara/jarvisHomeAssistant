import random, string, typing
import time, threading
import logging
from include.config import logLevel, AWSlogLevel
from include.utils import srcPath, singleton
import paho.mqtt.client as paho


@singleton
class MQTTclient():

    def __init__(self) -> None:
        """ 
		This os a simple wrapper for PAHO mqtt library.
		"""
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',level=logLevel)
        self.logger = logging.getLogger("JarvisBrainMQTTClient")
        self.client = paho.Client("JarvisBrain"+''.join(random.choices(string.ascii_uppercase + string.digits, k=5)), userdata=self)
        self.logger.info("Initializing MQTT client...")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("home-server", 1883, 60)
        self.loop_start()
        
    @staticmethod
    def on_message(client, userdata, msg):
        userdata.logger.warning(f"Message received on UNREGISTERED topic {msg.topic}: {msg.payload.decode()}")

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            userdata.logger.info(f"Connected successfully with code {rc}.")
        else:
            userdata.logger.error(f"Connection failed with code {rc}.")
            
    def subscribe(self, topic, callback = None, qos=2):
        if callback:
            self.client.message_callback_add(topic, callback)
        return self.client.subscribe(topic, qos)
    
    def publish(self, topic, payload, qos=2):
        return self.client.publish(topic, payload, qos)

    def loop_start(self):
        self.client.loop_start()    