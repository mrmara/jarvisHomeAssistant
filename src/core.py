from jarvis import jarvis
import time
import logging
from myMqttClient import MQTTclient
import threading

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
j = jarvis()
while True:
    time.sleep(1)
#j.process_command(j.listen_and_recognize())

