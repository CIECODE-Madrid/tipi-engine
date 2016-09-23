from send_email import emailSparkPost
from setting import DOMAIN
from database.congreso import Congress
import pdb

class NotifyTipi(object):
    _dbmanager = Congress()
    def __init__(self):
        self.sendAlerttousers()
        self.deleteAll()

    def sendAlerttousers(self):
        tipisalerts =  self._dbmanager.getTipisAllAlerts()
        userswithalerts = self._dbmanager.getUserswithAlert()
        for user in userswithalerts:
            alerttoshow=[]
            for alert in tipisalerts:
                #dict with name dict with list element
                #example sanidad:[item1,item2,item3]
                if alert['dict'] in user['profile']['dicts']:
                    objects = self.getObjects(alert['items'])
                    alertsanditems = dict()
                    alertsanditems[alert['dict']]=objects
                    alerttoshow.append(alertsanditems)
            #send one email to user with summary
            if alerttoshow:
                emailSparkPost.send_mail(user['emails'][0]['address'],alerttoshow)
    def deleteAll(self):
        self._dbmanager.deletecollection("tipialerts")

    def getObjects(self,objs):
        res=[]
        for obj in objs:
            newobj = dict()
            newobj['titulo']=obj['alert_titulo']
            newobj['url']="{0}/{1}".format(DOMAIN,str(obj['alert_id']))
            newobj['fecha']=obj["alert_fecha"]
            res.append(newobj)
        return res