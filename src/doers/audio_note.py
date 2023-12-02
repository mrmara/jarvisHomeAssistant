from datetime import datetime, timedelta
import threading, time
import include.interrupts as interrupts

class audio_note():
    def __init__(self, logger, note, date, topic):
        self.logger = logger
        self.logger.debug("STARTED AUDIO NOTE")
        self.note = ''.join(note)
        self.days_word = ["Today", "Tomorrow"]
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.date = self.decompose(date)
        self.client_topic = topic
        self.target_timestamp = self.retrieve_time()
        if self.target_timestamp != None:
            self.logger.debug(self.target_timestamp)
            x = threading.Thread(target=self.start_timer)
            x.start()
        else:
            self.logger.debug("INVALID")
        
    def decompose(self, date):
        res = {}
        for word in date:
            if word.capitalize() in self.days_word or word in self.weekdays:
                res["day"] = word
            elif ":" in word:
                res["hour"] = word.split(":")
                for i in range(0,len(res["hour"])):
                    res["hour"][i]= int(res["hour"][i])
                    
        return res
    
    def retrieve_time(self):
        if self.date["day"].capitalize() == self.days_word[0]:
            current_ts = time.time()
            target_ts = datetime.now().replace(hour=self.date["hour"][0], minute=self.date["hour"][1], second=0, microsecond=0).timestamp()
            if target_ts-current_ts > 0:
                return target_ts-current_ts
            else:
                return None
        elif self.date["day"].capitalize() == self.days_word[1]:
            #@TODO Fix bug in case of month change
            current_ts = time.time()
            target_ts = datetime.now().replace(day=datetime.now().day+1, hour=self.date["hour"][0], minute=self.date["hour"][1], second=0, microsecond=0)
            if target_ts-current_ts > 0:
                return target_ts-current_ts
            else:
                return None
        elif self.date["day"].capitalize() in self.weekdays:
            pass
    
    def start_timer(self):
        try:
            elapsed = 0
            while elapsed < self.target_timestamp:
                self.logger.debug("WAIT: ")
                self.logger.debug(self.target_timestamp-elapsed)
                time.sleep(1.0)
                elapsed+=1 
            interrupts.poll_list_mutex.acquire()
            for item in interrupts.poll_list:
                if (item[0] == self):
                    self.logger.info(f"asking for poll")
                    item[1] = interrupts.interrupt_status.POLLME
                    break
            interrupts.poll_list_mutex.release()
        except:
            pass
        
    def poll_me(self):
        self.logger.info(f"Allarm TIME")
        interrupts.poll_list_mutex.acquire()
        for item in interrupts.poll_list:
            if (item[0] == self):
                self.logger.info(f"removing from poll list")
                interrupts.poll_list.remove(item)
        interrupts.poll_list_mutex.release()
        return {"topic" : self.client_topic, "response" : self.note+", sir"}