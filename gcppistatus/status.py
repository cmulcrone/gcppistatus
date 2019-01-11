import requests
# import json


class status:

    severity_weights = {
        'low': lambda x: x * 1,
        'medium': lambda x: x * 2,
        'high': lambda x: x * 3,
    }

    def __init__(self, mode):
        self.mode = mode
        self.severity_value = 0
        self.recency_value = 0
        self.incident_volume = 0

    def hello_world(self):
        return 'hello world'

    def getJSON(self, url):
        response = requests.get(url)
        status = response.json()
        return status

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

    
    def score_severity(player):
        score = 0
        for stat in player._stats:
            if stat in scoring:
                score += scoring[stat](getattr(player,stat))    
        return score
