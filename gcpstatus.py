#Source List
#http://bsou.io/posts/color-gradients-with-python

import requests
import random
import math
import time
import datetime
import dateutil.parser
import _thread
import board
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy

NUMPIXELS = 64 #Number of neopixels
PI_PIN = board.D18 #Raspberry PI data pin 
BRIGHTNESS = 1.0 #Neopixel default brightness
STATUS_CHECK_DELAY = 10 #Delay between polling for updated status JSON
SEVERITY_VALUE = 0.0 #Global severity value to be passed between threads
HEALTHY_COLOR = fancy.CRGB(0.0, 1.0, 0.0) #Color for healthy GCP status
UNHEALTHY_COLOR = fancy.CRGB(1.0, 0.0, 0.0) #Color for unhealthy GCP status

class gcpstatus:

    def __init__(self):
        self.url = 'https://status.cloud.google.com/incidents.json'
        self.status = 'public'

    def getStatus(self):
        ps = status(self.status, self.url)
        return ps

class status:

    def __init__(self, mode, url, check_period = 30):
        self.mode = mode
        self.url = url
        self.json = self.getJSON()
        self.check_period = check_period
        self.severity_value = self.calculateSeverity(self.json)
        self.recency_value = self.calculateRecency(self.json)
        self.incident_volume = 0
    
    #Returns JSON of the URL passed (default public GCP status dashboard)
    def getJSON(self):
        try:
            response = requests.get(self.url)
            jsontext = response.json()
        except ValueError:
            return 'Error Decoding JSON'
            # TODO - set error state for Neopixel notification
        except requests.exceptions.ConnectionError:
            return "ConnectionError"
            # TODO - set error state for Neopixel notification
        except requests.exceptions.HTTPError:
            return False
            # TODO - set error state for Neopixel notification
        return jsontext

    #Returns relative value of service health in the past 30 days compared to the past year
    def calculateSeverity(self, jsontext):
        #Lambda for weighting severity of individual incidents
        severity_weights = {
            'low': lambda x: x * 1,
            'medium': lambda x: x * 2,
            'high': lambda x: x * 3,
        }

        #Date time for time period of measurements
        margin = datetime.timedelta(days = self.check_period)
        today = datetime.date.today()

        #Initialze dict holding historical severity scores, current score, and period counter
        severity_score_dict = {}
        severity_score_current = 0
        m = 1

        #While there are still status updates in the json, calculate and tally severity score by period
        for status in jsontext:
            statusdate = dateutil.parser.parse(status['begin'])

            #If the begin date is older than current period, dump current severity score into dict
            #and increment counter.  Otherwise, add severity score to current period total
            if not today - (margin * m) <= statusdate.date():
                severity_score_dict[m] = severity_score_current
                severity_score_current = severity_weights[status['severity']](1)
                m += 1
            else:
                severity_score_current += severity_weights[status['severity']](1)

        #Find minimum and maximum severity scores over the past year
        valmax = severity_score_dict[max(severity_score_dict.keys(), key=(lambda k: severity_score_dict[k]))]
        valmin = severity_score_dict[min(severity_score_dict.keys(), key=(lambda k: severity_score_dict[k]))]

        #TODO: Figure out how to handle month to month instead of in relation to the last year
        return (severity_score_dict[1] - valmin) / (valmax - valmin)

    def calculateRecency(self, jsontext):
        recency_weights = {
            'low': lambda x: x * 1,
            'medium': lambda x: x * 2,
            'high': lambda x: x * 3,
        }

        recency_score = 0
        for status in jsontext:
            if status['severity'] in recency_weights:
                recency_score += recency_weights[status['severity']](1)
        return recency_score

#Thread function that periodically checks the public GCP status JSON 
def status_check( threadName ):
    global SEVERITY_VALUE
    global STATUS_CHECK_DELAY

    timer = time.time()
    while True:
        if time.time() - timer > STATUS_CHECK_DELAY:
            currentStatus = gcpstatus().getStatus()
            SEVERITY_VALUE = currentStatus.severity_value
            print("SevValue=",SEVERITY_VALUE)

#Thread function to control light behavior based on valus set in status_check
def run_lights( threadname, ):
    global SEVERITY_VALUE
    global NUMPIXELS
    global BRIGHTNESS
    global HEALTHY_COLOR
    global UNHEALTHY_COLOR

    pixels = neopixel.NeoPixel(board.D18, NUMPIXELS, auto_write=False, brightness=BRIGHTNESS)

    intensity = round(SEVERITY_VALUE*63)
    print("Intensity=",intensity)
    grad = [ (0.0, HEALTHY_COLOR),
             (1.0, UNHEALTHY_COLOR) ]
    palette = fancy.expand_gradient(grad, 64)
        
    #TODO: Figure out how to clip this value to allow for dimming
    MAXIMUMBRIGHT=1.0
    #TODO: Figure out relationship of speed to duty cycle for calculating steps in the loop
    SPEED=.01
    #i=0
    while True:
        intensity = round(SEVERITY_VALUE*63) 
        color = fancy.palette_lookup(palette, (intensity/100)) 
        seconds = time.time()
        #blevel = float(i) / 10.0
        #TODO: See if you can simplify this code? Check spreadsheet
        #TODO: Add "breathing" mode
        #testblevel = math.exp(
        #TODO: Update idle, startup, and internet not found to rotate G Colors
        #TODO: Use seconds % SOMEVALUE to control frequency
        testblevel = (MAXIMUMBRIGHT / 2.0 * (1.0 + math.sin(SPEED * seconds)))/MAXIMUMBRIGHT
        print("SINE Value=", testblevel)
        #print("Time since epoch",time.time())
        levels = (testblevel, testblevel, testblevel)
        color = fancy.gamma_adjust(color, brightness=levels)
        #print("Color=",color)
        pixels.fill(color.pack())
        pixels.show()
        #i+=1

_thread.start_new_thread( status_check, ("StatusCheck Thread", ))
_thread.start_new_thread( run_lights, ("Running Lights Thread", ))

while 1:
    pass

#TODO: Add code to only work during business hours (limit bandwidth usage)
#while True:
    # Update status once every 5 secs
#    if time.time() - timer > 5:
#        print(currentStatus.severity_value)
#        timer = time.time()
#        pixels[m] = (255,0,0)
#        m += 1
