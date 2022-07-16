from recognizer import recognizer as jc
from include.utils import srcPath
from include.houndify import client_id,client_key
from jarvis import jarvis
import time
import logging
from myMqttClient import MQTTclient
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
#engine = jc(apiType=4,client_id=client_id,client_key=client_key,language='it-IT',initActivationWordListener=False)
#j = jarvis()
#j.process_command(engine.listen_and_recognize())
MQTTclient()

