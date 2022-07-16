from include.config import activation_words
import speech_recognition as sr
import include.customErrors as er
import logging
import threading
import time

class recognizer():

    def __init__(self, apiType: 'bing, google, google_cloud, houndify, ibm, sphinx, wit', key=None, credentials=None, language='en-US',
                    show_all=False, client_id=None, client_key=None, username ='', password='', keyword_entries=None, grammar=None, initMic = True,
                    initActivationWordListener = True) -> "Recognizer":
        super().__init__()
        self.apiType = apiType
        self.engine = sr.Recognizer()
        self.key=key
        self.credentials=credentials
        self.language=language
        self.show_all=show_all
        self.client_id=client_id
        self.client_key=client_key
        self.username=username
        self.passowrd=password
        self.keyword_entries=keyword_entries
        self.grammar=grammar
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        if initMic:
            self.init_microphone()
        if initActivationWordListener:
            x = threading.Thread(target=self.activation_word_listener)
            x.start()

    
    def recognize(self, audio_data) -> 'str':
        if self.apiType == 1:
            return self.engine.recognize_bing(audio_data=audio_data,key=self.key,language=self.language,show_all=self.show_all)
        elif self.apiType == 2:
            self.logger.debug("Recognizing with Google")
            return self.engine.recognize_google(audio_data=audio_data,key=self.key, language=self.language,show_all=self.show_all)
        elif self.apiType == 3:
            return self.engine.recognize_google_cloud(audio_data=audio_data, credentials_json=self.credentials, language=self.language)
        elif self.apiType == 4:
            self.logger.debug("Recognizing with Houndify")
            return self.engine.recognize_houndify(audio_data=audio_data, client_id=self.client_id, client_key=self.client_key, show_all=self.show_all)
        elif self.apiType == 5:
            return self.engine.recognize_ibm(audio_data=audio_data, username=self.username, password=self.password, language=self.language, show_all=self.how_all)
        elif self.apiType == 6:
            return self.engine.recognize_sphinx(audio_data, language=self.language, keyword_entries=self.keyword_entries, grammar=self.grammar, show_all=self.show_all)
        elif self.apiType == 7:
            return self.engine.recognize_wit(audio_data, key=self.key, show_all=False)
        else:
            raise er.RecognizerAPIError()

    def AudioFile(self, source: 'path or stream') -> 'AudioFile':
        self.audioIn = sr.AudioFile(source)
        return self.audioIn
    
    def record(self, source: 'audio file'):
        self.audioRec = self.engine.record(source)
        return self.audioRec
    
    def init_microphone(self) -> "Microphone":
        self.microphone = sr.Microphone(device_index=7)
        return self.microphone
        
    def activation_word_listener(self):
        while(True):
            self.listen()
            self.last_recognized_rec = self.recognize(self.last_rec)
            self.logger.debug(f"last record is {self.last_recognized_rec}")
            for word in self.last_recognized_rec.split(" "):
                if word in activation_words:
                    self.logger.info("Jarvis is awake")
                    self.listen_command()
    def listen(self):
        self.logger.debug("I am listening")
        with self.microphone as source:
            self.last_rec=self.engine.listen(source)
        self.logger.debug("I stopped listening")
        return self.last_rec

    def command(self, rec):
        com = self.recognize(rec)
        self.logger.debug(com)

    def listen_and_recognize(self):
        self.logger.debug("Understanding command")
        com = self.recognize(self.listen())
        return com.split(" ")