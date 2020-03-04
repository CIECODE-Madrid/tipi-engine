from database.congreso import Congress

'''
This class gets all urls and transform them to get a unique url
Note: Urls we save on scrap step are not unique because
they are based on a batch encoding
'''
class ConvertURLs():

    def convert(self):
        dbmanager = Congress()
        for initiative in dbmanager.getInitiatives():
           dbmanager.updateInitiativeURL(initiative['_id'], initiative['reference']) 
