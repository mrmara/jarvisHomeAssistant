import random, string
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os
import logging
from include.config import logLevel
from include.utils import srcPath
import signal

class MQTTclient():
    # Define ENDPOINT, CLIENT_ID_BASE, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT
    ENDPOINT = "a33k3qhzx4b7nb-ats.iot.us-east-1.amazonaws.com"
    CLIENT_ID_BASE = "Jarvis_"+ ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    PATH_TO_CERT = "cert/jarvis-certificate.pem.crt"
    PATH_TO_KEY = "cert/jarvis-private.pem.key"
    PATH_TO_ROOT = "cert/root.pem"
    PORT = 443

    def __init__(self) -> None:
        """ 
		This method initializes aws IoT.

		This method connects to aws IoT and create a subscription for the desired topic.
		# TODO: reconnection 
		"""
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',level=logLevel)
        self.logger = logging.getLogger("JarvisMQTTClient")
		# Spin up resources
        # Init AWSIoTMQTTClient
        myAWSIoTMQTTClient = None
        if self.PORT == 443:
            myAWSIoTMQTTClient = AWSIoTMQTTClient(self.CLIENT_ID_BASE, useWebsocket=True)
            myAWSIoTMQTTClient.configureEndpoint(self.ENDPOINT, self.PORT)
            myAWSIoTMQTTClient.configureCredentials(self.PATH_TO_ROOT)
        elif self.PORT == 8883:
            myAWSIoTMQTTClient = AWSIoTMQTTClient(self.CLIENT_ID_BASE)
            myAWSIoTMQTTClient.configureEndpoint(self.ENDPOINT, self.PORT)
            myAWSIoTMQTTClient.configureCredentials(self.PATH_TO_ROOT, self.PATH_TO_KEY, self.PATH_TO_CERT)

        # AWSIoTMQTTClient connection configuration
        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

        # Connect and subscribe to AWS IoT
        myAWSIoTMQTTClient.connect()

        self.logger.info(" Connecting to {} with client ID '{}'...".format(
				self.ENDPOINT, self.CLIENT_ID_BASE))
		# Future.result() waits until a result is available
        self.logger.info(" Connected!")
        myAWSIoTMQTTClient.subscribe("test", 1, self.on_message)
    
    def on_message(client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")

    