from include.basic_doer import *
from datetime import datetime, timedelta
import re
import json
from threading import Thread
from time import sleep


class Remember(Doer):

    def __init__(self, logger: logging.Logger):
        if not self.__class__._INITIALIZED:
            super().__init__(logger.getChild("remember"))
            self.start_checking_reminders()

    def start_checking_reminders(self):
        Thread(target=self.check_reminders).start()

    def check_reminders(self):
        while True:
            try:
                with open("reminders.json", "r+") as file:
                    try:
                        reminder_file: dict = json.load(file)
                    except json.JSONDecodeError:
                        reminder_file = {}

                    for reminder in list(reminder_file.keys()):
                        if float(reminder) - datetime.now().timestamp() < 0:
                            self.logger.info(
                                f"Reminder: {reminder_file[reminder]} is due at {float(reminder)} and now is {datetime.now().timestamp()}"
                            )
                            self.set_poll_payload(
                                f"Reminder: {reminder_file[reminder]}"
                            )
                            self.update_poll_status(interrupts.interrupt_status.POLLME)
                            reminder_file.pop(reminder)
                        else:
                            print(
                                f"Reminder: {reminder_file[reminder]}, time left {float(reminder) - datetime.now().timestamp()}"
                            )

                    file.seek(0)
                    json.dump(reminder_file, file)
                    file.truncate()
            except FileNotFoundError:
                with open("reminders.json", "w") as file:
                    json.dump({}, file)

            sleep(1)

    def do(self, speechTxt, client_topic):
        self.set_poll_topic(client_topic)
        self.logger.debug("remember intent")
        if self.get_poll_status() == interrupts.interrupt_status.CONVERSATION:
            self.conversation(speechTxt, client_topic)
        else:
            self.set_poll_payload("When do you want me to remind you?")
            self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
            self.date_needed = True
            self.time_needed = True

    def conversation(self, speechTxt, client_topic):
        super().conversation(speechTxt, client_topic)
        if self.date_needed:
            date_str = self.extract_date(speechTxt)
            if date_str is not None:
                self.logger.info(f"Extracted date: {date_str}")
                self.date_str = date_str
                self.set_poll_payload("At what time do you want me to remind you?")
                self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
                self.date_needed = False
            else:
                self.logger.warning("No valid date found in speech text.")
                self.set_poll_payload(
                    "Please provide a valid date in the format dd/mm/yyyy."
                )
                # Infinite loop unitl a valid date is provided
                self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
        elif self.time_needed:
            time_str = self.extract_time(speechTxt)
            if time_str is not None:
                self.logger.info(f"Extracted time: {time_str}")
                self.time_str = time_str
                self.time_needed = False
                self.set_poll_payload("What do you want me to remind you?")
                self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
            else:
                self.logger.warning("No valid time found in speech text.")
                self.set_poll_payload(
                    "Please provide a valid time in the format hh:mm."
                )
                # Infinite loop unitl a valid time is provided
                self.update_poll_status(interrupts.interrupt_status.CONVERSATION)
        else:
            self.logger.info(f"Reminder: {speechTxt}")
            self.reminder = " ".join(speechTxt)
            timestamp = self.convert_to_timestamp(self.date_str, self.time_str)
            self.set_poll_payload(
                f"I will remind you:\n {self.reminder}\n at {self.time_str} on {self.date_str} [{timestamp}]"
            )
            # Write to a JSON file the reminder as a value and the timestamp as a key
            try:
                with open("reminders.json", "r+") as file:
                    try:
                        reminders_file = json.load(file)
                    except json.JSONDecodeError:
                        reminders_file = {}
                    reminders_file[timestamp] = self.reminder
                    file.seek(0)
                    json.dump(reminders_file, file)
                    file.truncate()
            except FileNotFoundError:
                with open("reminders.json", "w") as file:
                    reminders_file = {timestamp: self.reminder}
                    json.dump(reminders_file, file)
            self.update_poll_status(interrupts.interrupt_status.WORKING)

    def extract_time(self, speechTxt):
        # Join the list into a single string
        speech_str = " ".join(speechTxt)

        # Regular expression to find hour and minute
        hour_pattern = r"\b(\d{1,2})\b"
        minute_pattern = r"\b(\d{1,2})\b"

        hour = None
        minute = None

        # Find all numbers in the speech text
        numbers = re.findall(r"\b\d+\b", speech_str)

        # Try to identify hour and minute
        for number in numbers:
            num = int(number)
            if 0 <= num <= 23 and hour is None:
                hour = f"{num:02d}"
            elif 0 <= num <= 59 and minute is None:
                minute = f"{num:02d}"

        if hour and minute:
            return f"{hour}:{minute}"
        return None

    def extract_date(self, speechTxt):
        # Join the list into a single string
        speech_str = " ".join(speechTxt)

        # Regular expression to find day, month, and year
        day_pattern = r"\b(\d{1,2})\b"
        month_pattern = r"\b(\d{1,2})\b"
        year_pattern = r"\b(\d{4})\b"

        day = None
        month = None
        year = None

        # Find all numbers in the speech text
        numbers = re.findall(r"\b\d+\b", speech_str)

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
