import requests
import time
import datetime
import dateutil.parser
import threading


def getStatus(self):
    ps = status(self.status, self.url)
    return ps

timer = time.time()

#TODO: Add code to only work during business hours (limit bandwidth usage)
while True:
    # Update status once every 5 secs
    if time.time() - timer > 1:
        print("#")
        timer = time.time()