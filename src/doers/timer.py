import time
import threading
class timer():
    def __init__(self, logger, mins, secs):
        self.logger = logger
        self.logger.info(f"Timer of {mins} minutes and {secs} seconds STARTED")
        self.total_secs = secs + mins*60
        x = threading.Thread(target=self.start_timer)
        x.start()
    
    def start_timer(self):
        self.remaining_secs = self.total_secs
        self.stop_timer = False
        while (self.remaining_secs) and not self.stop_timer:
            time.sleep(1)
            self.remaining_secs -= 1
    
    def get_remaining_time(self):
        mins, secs = divmod(self.remaining_secs, 60)
        return [mins, secs]

    def cancel_timer(self):
        self.stop_timer = True

        