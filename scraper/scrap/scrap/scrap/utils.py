import re
import urlparse
import pdb
import datetime


class Utils(object):
    @staticmethod
    def concatlist(list):
        if list:
            return '<br><br>'.join( elem for elem in list)
        else:
            return ''
    @staticmethod
    def dellastelement(list):

        del list[-1]
        return list
    @staticmethod
    def delfirstelement( list):

        del list[0]
        return list

    @staticmethod
    def getnumber(url):
        try:
            found = re.search('gina(.+?)\)', url).group(1)
        except:
            found = False
        return found

    @staticmethod
    def removeHTMLtags(text):
        TAG_RE = re.compile(r'<[^>]+>')
        BLANK = re.compile(r'\n\n ')
        BLANK2 = re.compile(r'\n ')
        BLANK3 = re.compile(r'  ')
        text = TAG_RE.sub('', text)
        text = BLANK.sub('', text)
        text = BLANK3.sub(' ', text)
        return BLANK2.sub('', text)
    @staticmethod
    def removeForDS(text):
        TAG_RE = re.compile(r'<[^>]+>')
        BLANK = re.compile(r'\n\n ')
        BLANK2 = re.compile(r'\n ')
        PAGES = re.compile(r'.*gina\n .*[0-9]\n\n')
        text = PAGES.sub('',text)
        text = TAG_RE.sub('', text)
        text = BLANK.sub('', text)
        return BLANK2.sub('', text)

    @staticmethod
    def checkPage(line, number):
        control = True
        regexps = ["gina" + number + '\)','name=']

        for rege in regexps:
            if not re.search(rege,line):
                control= False
                break
        return control
    @staticmethod
    def checkownRef(line, ref):
        control = True
        if not re.search(ref,line):
            control = False
        return control
    @staticmethod
    def checkotherRef(line):
        control = True
        if not re.search('[0-9]{3}\/[0-9]{6}',line):
            control = False
        return control

    @staticmethod
    def checkotherRefandnotOwn(line,ref):
        control = False
        if re.search('[0-9]{3}\/[0-9]{6}',line) and not re.search(ref,line) :
            control = True
        return control

    @staticmethod
    def isDiferentFirstTime(line,ref):
        lista = re.findall('[0-9]{3}\/[0-9]{6}',line)
        for element in lista:
            if element != ref:
                return True
        return False

    @staticmethod
    def geturl(list):
        return list[1]

    @staticmethod
    def getserie(list):
        return list[0]
    @staticmethod
    def createUrl(base,href):
        url = urlparse.urljoin(base, href)
        return url
    @staticmethod
    def checkEnmiendainarray(array, serie):
        control = False

        for element in array:
             if (re.search('dice de enmiendas', element) and serie =="A")\
                    or ( (re.search('Enmiendas', element) and serie =="B") )\
                     or (re.search('dice de enmiendas', element) and serie =="B"):
                control=True
                break
        return control
    @staticmethod
    def checkMocionEnmiendas(array, serie):
        control = False

        for element in array:
             if ( (re.search('Enmiendas', element) and serie =="D") ):
                control=True
                break
        return control

    @staticmethod
    def checkTextodefinitivoarray(array):
        control = False
        for element in array:
            if re.search('aprobaci(.+?)n(.*?)definitiva', element,re.IGNORECASE):
                control = True
                break
        return control

    @staticmethod
    def checkTypewithAmendments(type):
        types =['proposici(.+?)n no de ley','proyecto de ley','iniciativa legislativa popular',
                'moci(.+?)n','proposici(.+?)n de ley','proposici(.+?)n de reforma del reglamento del congreso']
        control = False
        for ty in types:
            if re.search(ty, type , re.IGNORECASE):
                control = True
                break
        return control

    @staticmethod
    def checkPreguntas(type):
        types = ["pregunta oral","respuesta escrita"]
        control = False
        for ty in types:
            if re.search(ty, type , re.IGNORECASE):
                control = True
                break
        return control

    @staticmethod
    def checkContestacion(array):
        for element in array:
            if  re.search("contestaci(.+?) del gobierno", element, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def clearTitle(string):
        res = re.sub('(\.?)([\(|\{].*?.$)|(.$)', '' , string.strip()).strip()
        res = re.sub('(.$)','',res.strip())
        BLANK = re.compile(r'\n')
        return BLANK.sub(' ', res)

    @staticmethod
    def hasSearchEnd(string):
        rexps = ["caducad(a|o)", "rechazad(a|o)", "aprobad(a|o)", "subsumid(o|a)", "tramitad(o|a)"
            , "inadmitid(o|a)", "concluid(o|a)", "retirad(o|a)"]

        control = False
        for rege in rexps:
            if re.search(rege, string, re.IGNORECASE):
                control = True
                break
        return control

    @staticmethod
    def getDateobject(string):
        splitdate = string.split('/')
        if len(splitdate) is 3:
            try:
                object = datetime.datetime(int(splitdate[2]),int(splitdate[1]),int(splitdate[0]))
            except:
                object = "Desconocida"
        else:
            object="Desconocida"
        return object
    @staticmethod
    def convertPagToNum(list):
        return [Utils.getnumber(element) for element in list]

