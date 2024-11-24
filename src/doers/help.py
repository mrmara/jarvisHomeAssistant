from include.basic_doer import *
import json
class Help(Doer):

    def __init__(self, logger: logging.Logger):
        if not self.__class__._INITIALIZED:
            super().__init__(logger.getChild("help"))
            self.intents = json.load(open("include/intents.json"))
            
    def do(self, speechTxt, client_topic):
        self.set_poll_topic(client_topic)
        self.logger.debug("help intent")
        response = "I can do the following things: "
        for key in self.intents.keys():
            response += key + ", "
        response = response[:-2] + "."
        self.set_poll_payload(response)
        self.update_poll_status(interrupts.interrupt_status.POLLME, exhausted=True)