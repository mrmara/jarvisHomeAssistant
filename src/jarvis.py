from time import sleep
from include.utils import srcPath
import json
from word2number import w2n
import logging
from myMqttClient import MQTTclient
from include.clients import clients_list
from doers.timer import timer
class jarvis:

    ongoing_timer = None
    
    def __init__(self):
        self.intents = json.load(open(srcPath() + "include/intents.json"))
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.mqtt = MQTTclient()
        for client in clients_list:
            self.mqtt.subscribe(client["name"]+"/request/#", self.on_message, qos=0)
            self.logger.info("Subscribed to %s topic", client["name"]+"/request/#")
            print("-------------------------")

    def on_message(self, client, userdata, message):
        self.logger.info("Received a new message: ")
        self.logger.info(message.payload)
        self.logger.info("from topic: ")
        self.logger.info(message.topic)
        self.logger.info("--------------\n\n")
        cmd = str(message.payload)
        print(cmd)
        cmd = cmd[3:-3]
        print(cmd)
        cmd = cmd.replace("'","").replace('"',"")
        print(cmd)
        cmd = cmd.split(", ")
        print(cmd)
        self.logger.info("commanding %s", cmd)
        self.process_command(cmd, message.topic)

    def process_command(self, speechTxt: 'list of command trascript words', client_topic):
        client_topic_ = client_topic
        got_command = False
        for word in speechTxt:
            self.logger.debug(word)
            if word in self.intents.keys():
                eval(self.intents[word]+"(speechTxt, client_topic_)")
                got_command = True
                break
        if not got_command:
            self.send_voice_response_to_client(client_topic, "I did not get you, sorry sir")
    
    def timer(self, speechTxt, client_topic):
        self.logger.debug("timer intent")
        self.logger.debug(speechTxt)
        secs =-1
        mins = -1
        for i in range(0, len(speechTxt)):
            if (speechTxt[i] == "remaining"):
                if (self.ongoing_timer != None):
                    remaining_time = self.ongoing_timer.get_remaining_time()
                    response = str(remaining_time[0]) + " minutes and " + str(remaining_time[1]) + " seconds, sir"
                    self.send_voice_response_to_client(client_topic, response)
                else:
                    response = str("There is not an active timer, sir")
                    self.send_voice_response_to_client(client_topic, response)

            elif (speechTxt[i] == "cancel"):
                if (self.ongoing_timer != None):
                    self.ongoing_timer.cancel_timer()
                    response = str("Done, sir")
                    self.send_voice_response_to_client(client_topic, response)
                else:
                    response = str("There is not an active timer, sir")
                    self.send_voice_response_to_client(client_topic, response)
            try:
                num = w2n.word_to_num(speechTxt[i])
                self.logger.debug(num)
                if (speechTxt[i+1]=="minutes" or speechTxt[i+1]=="minute"):
                    mins=num
                elif(speechTxt[i+1]=="seconds" or speechTxt[i+1]=="second"):
                    secs=num
            except:
                pass
        if (secs != -1 or mins != -1):
            self.ongoing_timer = timer(self.logger, mins, secs)
            self.send_voice_response_to_client(client_topic, "yes sir")
    
    def air_conditioner(self):
        pass

    def send_voice_response_to_client(self, topic, response):
        self.logger.info("Sending response %s", response)
        topic = topic.replace("/request","/response")
        self.mqtt.publish(topic, response)
    
