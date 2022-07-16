from include.utils import srcPath
import json
from word2number import w2n
import logging
from myMqttClient import MQTTclient

class jarvis:
    
    def __init__(self):
        self.intents = json.load(open(srcPath() + "include/intents.json"))
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.mqtt = MQTTclient()

    def process_command(self, speechTxt: 'list of command trascript words'):
        for word in speechTxt:
            self.logger.debug(word)
            if word in self.intents.keys():
                eval(self.intents[word]+"(speechTxt)")
                break
    
    def timer(self,speechTxt):
        self.logger.debug("timer")
        self.logger.debug(speechTxt)
        for word in speechTxt:
            try:
                self.logger.debug(w2n.word_to_num(word))
            except ValueError:
                pass
    
    def air_conditioner(self):
        pass
