#!/usr/bin/python3

import _thread
import time

blink_value = 1
status_check_delay = 5


# Define a function for the thread
def status_check( threadName, delay):
   global blink_value
   count = 0
   while count < 5:
      time.sleep(delay)
      count += 1
      blink_value = count

def blink_lights( threadName):
   while True:
      time.sleep(1)
      print (blink_value)

# Create two threads as follows
try:
   _thread.start_new_thread( status_check, ("Thread-1", 2, ) )
   _thread.start_new_thread( blink_lights, ("Thread-2", ) )
except:
   print ("Error: unable to start thread")

while 1:
   pass