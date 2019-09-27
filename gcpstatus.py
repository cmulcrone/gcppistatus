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

    def __init__(self, mode, url):
        self.mode = mode
        self.url = url
        self.json = self.getJSON()
        self.check_period = 30
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

        margin = datetime.timedelta(days = self.check_period)
        today = datetime.date.today()

        severity_score_dict = {}
        severity_score_current = 0
        m = 1

        for status in jsontext:
            statusdate = dateutil.parser.parse(status['begin'])

            if not today - (margin * m) <= statusdate.date():
                severity_score_dict[m] = severity_score_current
                severity_score_current = 0
                m += 1
            else:
                severity_score_current += severity_weights[status['severity']](1)

        valmax = severity_score_dict[max(severity_score_dict.keys(), key=(lambda k: severity_score_dict[k]))]
        valmin = severity_score_dict[min(severity_score_dict.keys(), key=(lambda k: severity_score_dict[k]))]

        #TODO: Figure out how to handle improvement (take absolute value?)
        z = (severity_score_dict[1] - severity_score_dict[2] - valmin) / (valmax - valmin)

        severity_score = 0

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