from time import sleep
import doers.timer, doers.help, doers.remember
from include.utils import srcPath
import json
import logging
from myMqttClient import MQTTclient
from include.clients import clients_list
import include.interrupts as interrupts
import threading
class jarvis:

    ongoing_timer = None
    
    def __init__(self):
        self.intents = json.load(open(srcPath() + "include/intents.json"))
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.mqtt = MQTTclient()
        self.speaker = None
        for client in clients_list:
            self.mqtt.subscribe(client["name"]+"/request/#", self.on_message, qos=0)
            self.logger.info("Subscribed to %s topic", client["name"]+"/request/#")
            self.logger.info("-------------------------")
        poller_ = threading.Thread(target=self.poller)
        poller_.start()
        
    def poller(self):
        self.logger.info("Poller started")
        while True:
            self.logger.debug(f"Polling list: {interrupts.poll_list}")
            for item in interrupts.poll_list:
                if (item[1] == interrupts.interrupt_status.POLLME):
                    self.logger.info("Polling %s", item[0])
                    ret = item[0].poll_me()
                    self.send_voice_response_to_client(ret["topic"], ret["response"])
                elif (item[1] == interrupts.interrupt_status.COMPLETED):
                    self.logger.info("Removing %s from poll list", item[0])
                    interrupts.remove_from_poll_list(item[0])
                elif (item[1] == interrupts.interrupt_status.CONVERSATION):
                    self.logger.info("Item %s is in conversation, starting the dialogue...", item[0])
                    self.speaker = item[0]
                    while item[1] == interrupts.interrupt_status.CONVERSATION:
                        ret = item[0].listen()
                        if ret is not None:
                            self.send_voice_response_to_client(ret["topic"], ret["response"])
                        sleep(1)
            sleep(1)
        
    def on_message(self, client, userdata, message):
        self.logger.info("Received a new message: ")
        self.logger.info(message.payload)
        self.logger.info("from topic: ")
        self.logger.info(message.topic)
        self.logger.info("--------------\n\n")
        
        # Decode the byte string to a regular string
        cmd = message.payload.decode('utf-8')
        cmd = cmd.replace("'", "").replace('"', "")
        cmd = cmd.split(" ")
        self.logger.info("Decoded command: %s", cmd)
        if self.speaker is not None:
            # There is a conversation ongoing
            self.speaker.do(cmd, message.topic)
        else:
            self.process_command(cmd, message.topic)

    def process_command(self, speechTxt: str, client_topic: str):
        client_topic_ = client_topic
        got_command = False
        for word in speechTxt:
            self.logger.debug(f"Currently processing word: {word}")
            if word in self.intents.keys():
                try:
                    eval("doers."+self.intents[word]+"(self.logger)"+".do(speechTxt, client_topic)")
                except Exception as e:
                    self.logger.error("Error processing command: %s", e)
                got_command = True
                break
        if not got_command:
            self.send_voice_response_to_client(client_topic, "I did not get you, sorry sir")
            
    def send_voice_response_to_client(self, topic, response):
        self.logger.info("Sending response %s", response)
        topic = topic.replace("/request","/response")
        self.mqtt.publish(topic, response)