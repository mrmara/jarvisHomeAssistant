from time import sleep
from include.utils import srcPath
import json
from word2number import w2n
import logging
from myMqttClient import MQTTclient
from include.clients import clients_list
from doers.timer import timer
from doers.audio_note import audio_note
import include.interrupts as interrupts
import threading
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
        poller_ = threading.Thread(target=self.poller)
        poller_.start()
        
    def poller(self):
        self.logger.info("Poller started")
        while True:
            for item in interrupts.poll_list:
                if (item[1] == interrupts.interrupt_status.POLLME):
                    self.logger.info("Polling %s", item[0])
                    ret = item[0].poll_me()
                    self.send_voice_response_to_client(ret["topic"], ret["response"])
        
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
            self.ongoing_timer = timer(self.logger, mins, secs, client_topic)
            interrupts.poll_list.append([self.ongoing_timer, interrupts.interrupt_status.WORKING])
            self.send_voice_response_to_client(client_topic, "yes sir")
            
    def help(self, speechTxt, client_topic):
        self.logger.debug("help intent")
        self.send_voice_response_to_client(client_topic, "I can do the following things: ")
        for key in self.intents.keys():
            self.send_voice_response_to_cjarvisHomeAssistant/src/doers/timer.py
    def send_voice_response_to_client(self, topic, response):
        self.logger.info("Sending response %s", response)
        topic = topic.replace("/request","/response")
        self.mqtt.publish(topic, response)
        
    def remember(self, speechTxt, client_topic):
        note = []
        hour = []
        is_between_to_and_day = False
        days_word = ["today", "tomorrow", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "on"]
        for string in speechTxt:
            if "to" == string:
                is_between_to_and_day = True
                continue
            
            for day in days_word:
                if day == string:
                    is_between_to_and_day = False
                    break

            if is_between_to_and_day:
                note.append(string)
                
        is_after_day = False     
           
        for string in speechTxt:
            
            for day in days_word:
                if day in string:
                    is_after_day = True
                    break
            if is_after_day:
                hour.append(string)
                
        self.logger.debug(note) 
        self.logger.debug(hour)
        inst = audio_note(self.logger, note, hour, client_topic)
        interrupts.poll_list.append([inst, interrupts.interrupt_status.WORKING])
        self.send_voice_response_to_client(client_topic, "yes sir")