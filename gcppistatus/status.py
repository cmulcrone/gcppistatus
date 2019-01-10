import requests
#import json

class status:

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
    def calculateMetrics(self, jsontext):
        severity_scores = {}
        for status in jsontext:
            if status['begin']:
                try: 
                    severity_scores[status['severity']] += 1
                except KeyError:
                    severity_scores[status['severity']] = 1
        return severity_scores

    severity_scoring = {  
        'low' : lambda x : x*1,
        'medium' : lambda x : x*3,
        'high' : lambda x : x*3,
    }


    def score_player(player):
        score = 0
        for stat in player._stats:
            if stat in scoring:
                score += scoring[stat](getattr(player,stat))    
        return score

    for week in weeks:
        with open('output/player_score/Week'+str(week)+'.csv', 'w') as csvfile:
            statwriter = csv.writer(csvfile, delimiter=',', \
                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            players = nflgame.combine_game_stats(nflgame.games(2017, week)) 
            for p in players:
                score = score_player(p)
                #Writes individual scores of users
                statwriter.writerow([week, p.playerid.encode(encoding='UTF-8'), \
                    p.name.encode(encoding='UTF-8'), \
                    p.guess_position.encode(encoding='UTF_8'), \
                    round(score,2)])
                '''print (week, p.playerid.encode(encoding='UTF-8'), \
                        p.name.encode(encoding='UTF-8'), \
                        p.guess_position.encode(encoding='UTF_8'), \
                        round(score,2))

        '''