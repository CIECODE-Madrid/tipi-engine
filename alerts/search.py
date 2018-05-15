from send_email import emailSparkPost
from settings import TIPIS_URL
import sys
sys.path.append("../")
from database.congreso import Congress
import pdb
import copy

class NotifyByEmail(object):

    dbmanager = Congress()

    def __init__(self):
        self.sendAlerttousers()
        self.deleteAll()

    def sendAlerttousers(self):
        alerts = self.dbmanager.getAllAlerts()
        userswithalerts = self.dbmanager.getUserswithAlert()
        for user in userswithalerts:
            alerttoshow = list()
            alerts_ = copy.copy(alerts)
            for alert in alerts_:
                if alert['topic'] in user['profile']['dicts']:
                    objects = self.getObjects(alert['items'])
                    alertsanditems = dict()
                    alertsanditems[alert['topic']] = objects
                    alerttoshow.append(alertsanditems)
            if alerttoshow:
                try:
                    emailSparkPost.send_mail(user['emails'][0]['address'],alerttoshow)
                except Exception,e:
                    print str(e)+" "+user['emails'][0]['address']+" is not a valid email"


    def deleteAll(self):
        self.dbmanager.deletecollection("alerts")

    def getObjects(self,objs):
        res=[]
        for obj in objs:
            newobj = dict()
            newobj['title'] = obj['title']
            newobj['url']="{0}{1}".format(TIPIS_URL,str(obj['id']))
            newobj['date'] = obj["date"]
            res.append(newobj)
        return res

if __name__ == "__main__":
    NotifyByEmail()
