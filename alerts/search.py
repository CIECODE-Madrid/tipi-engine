import json
import sys
sys.path.append("../")

from database.congreso import Congress
from send_email import emailSparkPost
from settings import TIPIS_URL


# Auxiliar function to transform from JSON unicode to Str
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


class NotifyByEmail(object):

    def __init__(self):
        self.dbmanager = Congress()
        self.sendAlerts()
        '''
        DESCOMENTAR ESTA LINEA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.dbmanager.deleteAllInitiativesAlerts()
        DESCOMENTAR ESTA LINEA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        '''

    def sendAlerts(self):
        alerts = self.dbmanager.getAllAlerts()
        for alert in alerts:
            for search in filter(lambda s: s['validated'], alert['searches']):
                initiatives = self.dbmanager.searchInitiativesAlerts(
                        byteify(json.loads(search['dbsearch']))
                        )
                print initiatives.count()


if __name__ == "__main__":
    NotifyByEmail()
