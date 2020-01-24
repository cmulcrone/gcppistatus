#Source List
#http://bsou.io/posts/color-gradients-with-python

import requests
import random
import math
import time
import datetime
import dateutil.parser
import _thread
import configparser
import board
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy

NUMPIXELS = 16 #Number of neopixels
PI_PIN = board.D18 #Raspberry PI data pin
MAXBRIGHTNESS = 1.0 #Neopixel default max brightness
STATUS_CHECK_DELAY = 10 #Delay between polling for updated status JSON
SEVERITY_VALUE = -1.0 #Global severity value to be passed between threads
RECENCY_VALUE = 2.0 #Recency value representing speed of breathing pattern
HEALTHY_COLOR = fancy.CRGB(0.0, 1.0, 0.0) #Color for healthy GCP status
MEDIUM_COLOR = fancy.CRGB(1.0, 0.7, 1.0) #Color for medium gradient
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
            pass
            #return 'Error Decoding JSON'
            # TODO - set error state for Neopixel notification
        except requests.exceptions.ConnectionError:
            return "ConnectionError"
            # TODO - set error state for Neopixel notification
        except requests.exceptions.HTTPError:
            pass
            #return False
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

        #Exit with no severity code if jsontext = ConnectionError
        if jsontext == 'ConnectionError':
            return -1.0

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
        recency_score = 0.0

        if jsontext == 'ConnectionError':
            return -1.0

        recent = next(iter(jsontext))
        statusdate = dateutil.parser.parse(recent['created'])
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - statusdate

        if delta.seconds < 80:
            recency_score = 0.2
        elif delta.seconds < 300:
            recency_score = 0.4
        elif delta.seconds < 900:
            recency_score = 0.6
        elif delta.seconds < 3600:
            recency_score = 0.8
        else:
            recency_score = 1.0

        return recency_score

#Rotating G-colors called when status connectivity not established
def loading_lights(pixels):
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    yellow = (255, 150, 0)

    #Loop through 
    for i in range(pixels.n):
        pixels[i] = red
        pixels[(i + math.floor(pixels.n / 4)) % pixels.n] = blue
        pixels[(i + math.floor(pixels.n / 4 * 2)) % pixels.n] = green
        pixels[(i + math.floor(pixels.n / 4 * 3)) % pixels.n] = yellow

        pixels.show()
        time.sleep(0.1)

#Controls lights that reflect current GCP status
def status_lights(pixels, palette, eul, inveul, brightness):
    global RECENCY_VALUE
    global SEVERITY_VALUE
    global NUMPIXELS
    global MAXBRIGHTNESS
    
    #Set color and brightness pattern frequency based on current values
    intensity = round(SEVERITY_VALUE*63)
    color = fancy.palette_lookup(palette, (intensity/100))
    seconds = time.time()
    frequency = RECENCY_VALUE
    floor = 0.1
    
    #Breathing pattern to control brightness
    testblevel = (math.exp(math.sin((seconds % 60)/frequency))-inveul)*(brightness/(eul-inveul))
    if testblevel > floor:
        led_level = testblevel
    else:
        led_level = floor

    #TODO: Use seconds % SOMEVALUE to control frequency
    #Simple sine wave
    #testblevel = (MAXIMUMBRIGHT / 2.0 * (1.0 + math.sin(SPEED * seconds)))/MAXIMUMBRIGHT
    #print("SINE Value=", led_level)

    levels = (led_level, led_level, led_level)
    color = fancy.gamma_adjust(color, brightness=levels)
    pixels.fill(color.pack())
    pixels.show()


#Thread function that periodically checks the public GCP status JSON 
def status_check( threadName ):
    global SEVERITY_VALUE
    global RECENCY_VALUE
    global STATUS_CHECK_DELAY

    #TODO: Add code to only work during business hours (limit bandwidth usage)
    timer = time.time()
    while True:
        if time.time() - timer > STATUS_CHECK_DELAY:
            currentStatus = gcpstatus().getStatus()
            SEVERITY_VALUE = currentStatus.severity_value
            RECENCY_VALUE = currentStatus.recency_value
            timer = time.time()
            print("SevValue=",SEVERITY_VALUE)
            print("RecValue=",RECENCY_VALUE)

#Thread function to control light behavior
def run_lights( threadname, ):
    global HEALTHY_COLOR
    global MEDIUM_COLOR
    global UNHEALTHY_COLOR
    global SEVERITY_VALUE
    global NUMPIXELS
    global MAXBRIGHTNESS

    #Initialize Neopixels
    pixels = neopixel.NeoPixel(board.D18, NUMPIXELS, auto_write=False, brightness=MAXBRIGHTNESS)

    #Set up gradient pallete and constant values
    grad = [ (0.0, HEALTHY_COLOR),
             (1.0, UNHEALTHY_COLOR) ]
    palette = fancy.expand_gradient(grad, 64)
    eul = math.e
    inveul = 1/math.e
    brightness = 0.8
    #TODO: Figure out relationship of speed to duty cycle for calculating steps in the loop
    #SPEED=1.0

    #Run loop
    while True:
        if SEVERITY_VALUE == -1.0:
            loading_lights(pixels)
        else:
            status_lights(pixels, palette, eul, inveul, brightness)

#Read config values from ini file and use to set global values
def read_configs():
    global STATUS_CHECK_DELAY
    global NUMPIXELS
    global MAXBRIGHTNESS
    global HEALTHY_COLOR
    global MEDIUM_COLOR
    global UNHEALTHY_COLOR

    config = configparser.ConfigParser()
    config.read('status.ini')
    
    STATUS_CHECK_DELAY = float(config['DEFAULT']['STATUS_CHECK_DELAY'])
    NUMPIXELS = float(config['DEFAULT']['NUMPIXELS'])
    MAXBRIGHTNESS = float(config['DEFAULT']['MAXBRIGHTNESS'])
    HEALTHY_COLOR = fancy.unpack(config['DEFAULT']['HEALTHY_COLOR'])
    MEDIUM_COLOR = fancy.unpack(config['DEFAULT']['MEDIUM_COLOR'])
    UNHEALTHY_COLOR = fancy.unpack(config['DEFAULT']['UNHEALTHY_COLOR'])


#Main function, kicks off status check and light control threads
def main():
    read_configs()
    _thread.start_new_thread( status_check, ("StatusCheck Thread", ))
    _thread.start_new_thread( run_lights, ("Running Lights Thread", ))

    while 1:
        pass

main()
