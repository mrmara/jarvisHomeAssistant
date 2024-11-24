from include.basic_doer import *
from datetime import datetime, timedelta
import re
import json

#add a thread for the following

        # reminder_file =  json.load(open("reminders.json", "r"))
        # for reminder in reminder_file:
        #     if abs(float(reminder) - datetime.now().timestamp()) < 30:
        #         self.logger.info(f"Reminder: {reminder_file[reminder]}")
        #         self.set_poll_payload(f"Reminder: {reminder_file[reminder]}")
        #         self.update_poll_status(interrupts.interrupt_status.POLLME, exhausted=True)
        #         reminder_file.pop(reminder)
        #         json.dump(reminder_file, open("reminders.json", "w+"))
                
                
class Remember(Doer):

    def __init__(self, logger: logging.Logger):
        if not self.__class__._INITIALIZED:
            super().__init__(logger.getChild("remember"))
            
    def do(self, speechTxt, client_topic):
        self.set_poll_topic(client_topic)
        self.logger.debug("remember intent")
        if self.get_poll_status() == interrupts.interrupt_status.CONVERSATION:
            self.conversation(speechTxt, client_topic)
        else:
            self.set_poll_payload("When do you want me to remind you?")
            self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
            self.date_needed = True
    
    def conversation(self, speechTxt, client_topic):
        if self.date_needed:
            date_str = self.extract_date(speechTxt)
            if date_str is not None:
                self.logger.info(f"Extracted date: {date_str}")
                self.date_str = date_str
                self.set_poll_payload("At what time do you want me to remind you?")
                self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
                self.date_needed = False
                self.time_needed = True
            else:
                self.logger.warning("No valid date found in speech text.")
                self.set_poll_payload("Please provide a valid date in the format dd/mm/yyyy.")
                self.update_poll_status(interrupts.interrupt_status.COMPLETED)
        elif self.time_needed:
            time_str = ':'.join(speechTxt)
            self.logger.info(f"Extracted time: {time_str}")
            self.time_str = time_str
            self.time_needed = False
            self.set_poll_payload("What do you want me to remind you?")
            self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
        else:
            self.logger.info(f"Reminder: {speechTxt}")
            self.reminder = ' '.join(speechTxt)
            self.timestamp = self.convert_to_timestamp(self.date_str, self.time_str)
            self.set_poll_payload(f"I will remind you:\n {self.reminder}\n at {self.time_str} on {self.date_str}")
            
            # write to a json file the reminder as a value and the timestamp as a key
            reminders_file = json.load(open("reminders.json", "r"))
            reminders_file[self.timestamp] = self.reminder
            json.dump(reminders_file, open("reminders.json", "w+"))
            self.update_poll_status(interrupts.interrupt_status.WORKING)

    def extract_date(self, speechTxt):
        # Join the list into a single string
        speech_str = ' '.join(speechTxt)
        
        # Regular expression to find day, month, and year
        day_pattern = r'\b(\d{1,2})\b'
        month_pattern = r'\b(\d{1,2})\b'
        year_pattern = r'\b(\d{4})\b'
        
        day = None
        month = None
        year = None
        
        # Find all numbers in the speech text
        numbers = re.findall(r'\b\d+\b', speech_str)
        
        # Try to identify day, month, and year
        for number in numbers:
            num = int(number)
            if 1 <= num <= 31 and day is None:
                day = f"{num:02d}"
            elif 1 <= num <= 12 and month is None:
                month = f"{num:02d}"
            elif 1000 <= num <= 9999 and year is None:
                year = str(num)
        
        if day and month and year:
            return f"{day}/{month}/{year}"
        return None
    
    def convert_to_timestamp(self, date_str, time_str):
        # Combine date and time strings into a single datetime object
        datetime_str = f"{date_str} {time_str}"
        dt = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M")
        # Convert to Unix timestamp
        timestamp = dt.timestamp()
        return timestamp