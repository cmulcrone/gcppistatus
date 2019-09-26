import requests
import time
import datetime
import dateutil.parser

class gcpstatus:

    def __init__(self):
        self.url = 'https://status.cloud.google.com/incidents.json'
        self.status = 'public'

    def getStatus(self):
        ps = status(self.status, self.url)
        return ps

class status:

    severity_weights = {
        'low': lambda x: x * 1,
        'medium': lambda x: x * 2,
        'high': lambda x: x * 3,
    }

    def __init__(self, mode, url):
        self.mode = mode
        self.url = url
        self.json = self.getJSON()
        self.severity_value = self.calculateSeverity(self.json)
        self.recency_value = self.calculateRecency(self.json)
        self.incident_volume = 0

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

    def calculateSeverity(self, jsontext):
        severity_weights = {
            'low': lambda x: x * 1,
            'medium': lambda x: x * 2,
            'high': lambda x: x * 3,
        }

        margin = datetime.timedelta(days = 90)
        today = datetime.date.today()

        severity_score = 0
        severity_score_previous = 0
        severity_score_current = 0
        for status in jsontext:
            statusdate = dateutil.parser.parse(status['begin'])
            
            if today - margin <= statusdate.date() and status['severity'] in severity_weights:
                severity_score_current += severity_weights[status['severity']](1)

            if today - margin*2 <= statusdate.date() <= today - margin and status['severity'] in severity_weights:
                severity_score_previous += severity_weights[status['severity']](1)
        
        severity_score = severity_score_current - severity_score_previous

        return severity_score

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

timer = time.time()
currentStatus = gcpstatus().getStatus()


while True:
    # Update status once every 5 secs
    if time.time() - timer > 5:
        print(currentStatus.severity_value)
        timer = time.time()