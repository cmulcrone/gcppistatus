import status
import neopixels
import time


class gcppistatus:

    def __init__(self):
        self.url = 'https://status.cloud.google.com/incidents.json'
        self.status = 'public'

    def runTheCloud(self, currentStatus):
        ps = status(self.status, self.url)

        while (True):
            try:
                # TODO - set neopixels based on metrics
                tmpPrint = 'Severity score:' + ps.severity_value
                print tmpPrint
                # TODO - Sleep
                time.sleep(60)
                # TODO - Refresh scores
                
            except Exception as e:
                raise
            else:
                pass
            finally:
                pass
