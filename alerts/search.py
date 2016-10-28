from send_email import emailSparkPost
from setting import TIPIS_URL
import sys
sys.path.append("../")
from database.congreso import Congress
import pdb
import copy

class NotifyTipi(object):
    _dbmanager = Congress()
    def __init__(self):
        self.sendAlerttousers()
        self.deleteAll()

    def sendAlerttousers(self):
        tipisalerts = self._dbmanager.getTipisAllAlerts()
        userswithalerts = self._dbmanager.getUserswithAlert()
        for user in userswithalerts:
            alerttoshow=list()
            copycursotalert= copy.copy(tipisalerts)
            for alert in copycursotalert:
                #dict with name dict with list element
                #example sanidad:[item1,item2,item3]alert['dict']
                if alert['dict'] in user['profile']['dicts']:
                    objects = self.getObjects(alert['items'])
                    alertsanditems = dict()
                    alertsanditems[alert['dict']]=objects
                    alerttoshow.append(alertsanditems)
            #send one email to user with summary
            if alerttoshow:
                try:
                        emailSparkPost.send_mail(user['emails'][0]['address'],alerttoshow)
                except Exception,e:
                        print str(e)+" "+user['emails'][0]['address']+" no es un email valido"


    def deleteAll(self):
        self._dbmanager.deletecollection("tipialerts")

    def getObjects(self,objs):
        res=[]
        for obj in objs:
            newobj = dict()
            newobj['titulo']=obj['titulo']
            newobj['url']="{0}{1}".format(TIPIS_URL,str(obj['id']))
            newobj['actualizacion']=obj["actualizacion"]
            res.append(newobj)
        return res
#if __name__ == "__main__":
#    a = NotifyTipi()
