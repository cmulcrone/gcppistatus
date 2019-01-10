import requests
import json

class status:
	def __init__(self, mode):
		self.mode = mode

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