import os
import queue
import time

from datetime import datetime as datetime # lol
from datetime import timedelta as timedelta 

from log_utils import * 

class Monitor(object):
    def __init__(self):
        # get the current time to base our triggers off of
        self.now = datetime.now()

        # Create a threshold queue that will hold LogItems in FIFO order. Items
        # will # be popped off the top if they are from before two minutes ago.
        # Keep a flag on the current threshold status.
        self.threshold_delta = timedelta(minutes=2)
        self.threshold_queue = queue.Queue()
        self.threshold = 20
        self.above_threshold = False

        # Create a display list that will hold LogItems. Everytime the event
        # loop crosses the next_display time,  show some stats on display list,
        # clear the list, and set next_display to 10 seconds from the last one.
        self.display_delta = timedelta(seconds=10)
        self.next_display = self.now + self.display_delta
        self.display_list = [ ] 

    def high_traffic_alert(self):
        message =  "HIGH TRAFFIC ALERT\n\tHits = %s\n\tTriggered at %s" % \
                (
                    len(self.threshold_queue.queue),
                    self.now.strftime("%A, %d. %B %Y %I:%M%p")
                )
        print(message)

    def low_traffic_alert(self):
        message = "TRAFFIC ALERT OVER\n\tTriggered at %s" % \
                self.now.strftime("%A, %d. %B %Y %I:%M%p")
        print(message)

    def display_stats(self):
        print("display stat")
        # do some processing for display
        for i, item in enumerate(self.display_list):
            a = "a"


    def start_loop(self, log_item_generator):
        while True:
            self.now = datetime.now()

            threshold_time = self.now - self.threshold_delta
            while not self.threshold_queue.empty() and \
                    self.threshold_queue.queue[0].time < threshold_time:
                _ = self.threshold_queue.get()

            threshold_size = len(self.threshold_queue.queue)
            if threshold_size > self.threshold:
                if not self.above_threshold:
                    self.above_threshold = True
                    self.high_traffic_alert()
            else:
                if self.above_threshold:
                    self.above_threshold = False
                    self.low_traffic_alert()

            if self.now > self.next_display:
                self.next_display = self.next_display + self.display_delta
                self.display_stats()
                self.display_list = [ ]

            try:
                log_item = log_item_generator.next_item()
                if log_item:
                    print("added")
                    self.threshold_queue.put(log_item)
                    self.display_list.append(log_item)
                else:
                    print(self.now.strftime("%A, %d. %B %Y %I:%M%p"))
                    time.sleep(2)
            except Exception as e:
                print("error creating log entry %s" % e)
            

if __name__ == '__main__':
    log_filename = os.path.join(
            # '/', 'var', 'log', 'nginx', 'access.log')
            os.path.dirname(__file__), '..', 'test_data', 'access.log')
    logger = LogTail(log_filename)

    monitor = Monitor()
    monitor.start_loop(logger)
