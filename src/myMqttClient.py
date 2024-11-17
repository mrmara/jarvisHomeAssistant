import random, string
import time
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os
import logging
from include.config import logLevel, AWSlogLevel
from include.utils import srcPath, singleton
import signal

@singleton
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
        self.myAWSIoTMQTTClient = None
        if self.PORT == 443:
            self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.CLIENT_ID_BASE, useWebsocket=True)
            self.myAWSIoTMQTTClient.configureEndpoint(self.ENDPOINT, self.PORT)
            self.myAWSIoTMQTTClient.configureCredentials(self.PATH_TO_ROOT)
        elif self.PORT == 8883:
            self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.CLIENT_ID_BASE)
            self.myAWSIoTMQTTClient.configureEndpoint(self.ENDPOINT, self.PORT)
            self.myAWSIoTMQTTClient.configureCredentials(self.PATH_TO_ROOT, self.PATH_TO_KEY, self.PATH_TO_CERT)
        logging.getLogger('AWSIoTPythonSDK').setLevel(AWSlogLevel)
        # AWSIoTMQTTClient connection configuration
        self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        # Connect and subscribe to AWS IoT
        self.myAWSIoTMQTTClient.connect()

        self.logger.info(" Connecting to {} with client ID '{}'...".format(
				self.ENDPOINT, self.CLIENT_ID_BASE))
		# Future.result() waits until a result is available
        self.logger.info(" Connected!")

    def subscribe(self, topic, callback, qos=0):
        return self.myAWSIoTMQTTClient.subscribe(topic, qos, callback)
    
    def publish(self, topic, payload, qos=0):
        return self.myAWSIoTMQTTClient.publish(topic, payload,qos)
    