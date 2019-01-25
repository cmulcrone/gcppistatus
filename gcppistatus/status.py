import requests
# import json


class status:

    severity_weights = {
        'low': lambda x: x * 1,
        'medium': lambda x: x * 2,
        'high': lambda x: x * 3,
    }

    def __init__(self, mode, url):
        self.mode = mode
        self.severity_value = self.calculateSeverity(self.getJSON())
        self.recency_value = 0
        self.incident_volume = 0
        self.url = url

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

        severity_score = 0
        for status in jsontext:
            if status['severity'] in severity_weights:
                severity_score += severity_weights[status['severity']](1)
        return severity_score

    '''
    Metrics -
        - Recency of last event
        - Severity score
        - Incident volume (maybe tie to recency)
        - Product area
    Visualizations -
        - Color
        - Brightness
        - Blinking/Strobe/Pulse
            - Speed
            - Pattern
            - Storm
    '''

    

    '''
    try:
        severity_scores[status['severity']] += 1
    except KeyError:
        severity_scores[status['severity']] = 1
    '''
