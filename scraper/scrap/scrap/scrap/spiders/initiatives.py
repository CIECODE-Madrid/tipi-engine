# -*- coding: utf-8 -*-
import re
import urlparse
import datetime
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from fuzzywuzzy import fuzz
import scrapy
from scrapy import Spider
from scrapy.selector import Selector
import pdb
from scrapy.spidermiddlewares.httperror import HttpError
from scrap.term import Terms
from scrap.items import InitiativeItem,AmendmentItem, FinishTextItem, ResponseItem
from twisted.internet.error import DNSLookupError, TimeoutError
from scrap.blacklist import Blacklist
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrap.utils import Utils
from scrap.mail import emailScrap
from scrap.check import CheckItems, CheckSystem
from scrap.typeamendment import AmendmentFlow
from database.congreso import Congress


class StackSpider(Spider):
    #item = InitiativeItem()
    name = "initiatives"
    allowed_domains = ["http://www.congreso.es/","www.congreso.es"]
    start_urls = [
        "http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas",
    ]
    time = None
    congress = None
    members = None
    groups = None
    def __init__(self,*a, **kw):
        super(StackSpider,self).__init__(*a, **kw)
        self.time = datetime.datetime.now()
        self.congress = Congress()
        self.members = self.congress.searchAll('deputies')
        self.groups = self.congress.searchAll('parliamentarygroups')
        dispatcher.connect(self.whenFinish, signals.spider_closed)

    def whenFinish(self):
        self.time = datetime.datetime.now() - self.time
        print("********  %s " % self.time)
        email = emailScrap()
        text = "Ha tardado: "+ (" %s " % self.time) +"\n\n<br>"
        text += '<br>'.join('{}{}{}'.format(key,"\t", val) for key, val in self.crawler.stats.get_stats().items())
        text += "\n\n\n"
        notscrap = CheckItems.checkUrls()
        CheckItems.deleteDb()
        email.send_mail(text, "Scrapy Stats")

    def start_requests(self):
        return [scrapy.FormRequest("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335505_73_1335500_1335500.next_page=/wc/cambioLegislatura",
                                   formdata = {'idLegislatura':'12'} , callback = self.parse)]

    def parse(self, response):

        list_types = Selector(response).xpath('//div[@class="listado_1"]//ul/li/a')
        for types in list_types:
            href=  types.xpath("./@href").extract()
            text = types.xpath("./text()").extract()
            if Terms.filterBytype(text[0]):
                type = Terms.getType(text[0])
                initiative_url = Utils.createUrl(response.url,href[0])
                yield scrapy.Request(initiative_url,errback=self.errback_httpbin,callback=self.initiatives, meta={'type': type})
        """
        urlsa = ""
        urlsa = "http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW12&PIECE=IWC2&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=100-100&QUERY=%28I%29.ACIN1.+%26+%28161%29.SINI."


        yield scrapy.Request(urlsa, errback=self.errback_httpbin, callback=self.oneinitiative,
                             meta={'type': u"Proposición no de Ley en Comisión"})
        """
        


    def initiatives(self, response):
        type = response.meta['type']
        first_url = Selector(response).xpath('//div[@class="resultados_encontrados"]/p/a/@href').extract()[0]
        num_inis = Selector(response).xpath('//div[@class="SUBTITULO_CONTENIDO"]/span/text()').extract()
        split = first_url.partition("&DOCS=1-1")
        for i in range(1,int(num_inis[0])+1):
            new_url = split[0]+"&DOCS="+str(i)+"-"+str(i)+split[2]
            initiative_url = Utils.createUrl(response.url,new_url)
            CheckItems.addElement(initiative_url)

            if not Blacklist.getElement(initiative_url):
                yield scrapy.Request(initiative_url,errback=self.errback_httpbin,
                                     callback=self.oneinitiative, meta = {'type':type})

    def oneinitiative(self,response):
        type = response.meta['type'] #initiative_type_alt
        try:
            title = Selector(response).xpath('//p[@class="titulo_iniciativa"]/text()').extract()[0]
            expt = re.search('\(([0-9]{3}\/[0-9]{6})\)', title).group(1)
        except:
            #refresco por si no carga
            yield scrapy.Request(response.url, errback=self.errback_httpbin, callback=self.oneinitiative,
                                 meta={'type': type})
        presentado = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="texto" and contains(text(),"Presentado")]').extract()
        aut = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"Autor:") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"Autor:")]]')
        aut1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"Autor:") ]/following-sibling::\
           p[@class="texto"]')
        ##DEPENDE DE DONDE ESTEN SITUADOS LOS BOLETINES
        #si no estan los ultimos
        bol = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and text()="Boletines:" ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[. = "Boletines:"]]')
        #si estan los ultimos
        bol1= Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and text()="Boletines:" ]/following-sibling::\
           p[@class="texto"]')
        ds = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and text()="Diarios de Sesiones:" ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[. = "Diarios de Sesiones:"]]')
        ds1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and text()="Diarios de Sesiones:" ]/following-sibling::\
           p[@class="texto"]')
        # para las tramitaciones
        tn = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"seguida por la iniciativa:") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"seguida por la iniciativa:")]]')
        tn1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"seguida por la iniciativa:") ]/following-sibling::\
           p[@class="texto"]')

                # para resultado de las  tramitaciones
        restr = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"ultado de la tramitac") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"Resultado de la tramitac")]]')
        restr1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"ultado de la tramitac") ]/following-sibling::\
           p[@class="texto"]')
        #para ponentes por si los hubiere
        pon = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"Ponentes:") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"Ponentes:")]]')
        pon1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"Ponentes:") ]/following-sibling::\
           p[@class="texto"]')
        com = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"n competente:") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"n competente:")]]')
        com1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"n competente:") ]/following-sibling::\
           p[@class="texto"]')
        #switch para saber si esta el ultimo o no
        boletines = None
        diarios = None
        tramitacion = None
        restramitacion= None
        ponentes = None
        comision = None
        autors=None

        if aut:
            autors = aut
        elif not aut:
            autors = aut1

        if bol:
            boletines = bol
        elif not bol:
            boletines = bol1

        if ds:
            diarios = ds
        elif not ds:
            diarios = ds1

        if tn:
            tramitacion = tn
        elif not tn:
            tramitacion = tn1

        if restr:
            restramitacion = restr
        elif not restr:
            restramitacion = restr1

        if pon:
            ponentes = pon
        elif not pon:
            ponentes = pon1
        if com:
            comision = com
        elif not bol:
            comision = com1

        listautors=[]

        for autor in (autors):
            add = autor.xpath("a/b/text()").extract()
            if not add:
                add = autor.xpath("./text()").extract()[0]
            else:
                add= add[0]
            listautors.append(re.sub('(([\(|\{].*?.$)|(y otr(os|as))|^(Don|Do(.+?)a))', '' , add).strip()) #quita () si lo hubiere
        if ponentes:
            for ponente in ponentes:
                add = ponente.xpath("a/b/text()").extract()
                if not add:
                    try:
                        add = ponente.xpath("./text()").extract()[0]
                        listautors.append(add)
                    except:
                        pass
                else:
                    if add:
                        add= add[0]
                        listautors.append(add)
        item = InitiativeItem()
        item['reference'] = expt
        item['title'] = Utils.clearTitle(title)
        item['url'] = response.url
        ##control autor
        item['author_deputies'] = []
        item['author_parliamentarygroups'] = []
        item['author_others'] = []
        for oneaut in listautors:
            typeaut = self.typeAutor(name=oneaut)
            if typeaut is 'deputy':
                item['author_deputies'].append(oneaut)
                try:
                    item['author_parliamentarygroups'].append(self.getParliamentaryGroupFromDeputy(name=oneaut)['name'])
                except:
                    CheckSystem.systemlog("Fallo en enmienda, no encuentra grupo parlamentario en la db" + response.url)
            elif typeaut is 'parliamentarygroup':
                item['author_parliamentarygroups'].append(oneaut)
            elif typeaut is 'other':
                item['author_others'].append(oneaut)
        #si hubiera varios autores del mismo grupo
        item['author_parliamentarygroups'] = list(set(item['author_parliamentarygroups']))
        item['initiative_type_alt'] = type
        item['initiative_type'] = re.search('[0-9]{3}', expt).group(0)

        item['content'] = []

        #si hay comisiones meter la comision(es donde se habla de las inicitativas
        if comision:
            comision = comision.xpath("./a/b/text()").extract()

        item['place'] = self.extractplace(DS = diarios, com = comision , type = type)
        item['processing'] = ""

        item['created'] = ""
        item['ended'] = ""
        try:
            if presentado:
                #se obtiene la fecha

                fechainicio = re.search('([0-9]{2}\/[0-9]{2}\/[0-9]{4}),', presentado[0]).group(1).strip() #se obtiene la fecha
                item['created'] = Utils.getDateobject(fechainicio)
                #control de fecha final
                if re.search('calificado el ([0-9]{2}\/[0-9]{2}\/[0-9]{4}) ', presentado[0]):
                    item['ended'] = Utils.getDateobject(re.search('calificado el ([0-9]{2}\/[0-9]{2}\/[0-9]{4}) ', presentado[0]).group(1))

            # else:
            #     item['created'] = "Fecha no encontrada"

        except:
             CheckSystem.systemlog("Falla al encontrar la fecha " + response.url)

        rtr = None
        tr = None
        if  tramitacion:
            #cogemos la ultima tramitacion
            tr = tramitacion.extract()[0].strip().split('<br>')[-1]
        if  restramitacion:
            #cogemos el ultimo resultado de la tramitacion
            rtr = restramitacion.extract()[0].strip().split('<br>')[-1]

        #instert tramitacion in item
        if rtr:
            item['processing'] = Utils.removeHTMLtags(rtr)
        elif tr:
            item['processing'] = Utils.removeHTMLtags(tr)
        else:
            item['processing'] = "Desconocida"

        #saber si se ha actualizado
        #search = self.congress.getInitiative(ref=item['reference'],initiative_type_alt=item['initiative_type_alt'],title=item['title'])
        #if search and ((not Utils.checkTypewithAmendments(type) and not Utils.checkPreguntas(type)) or  Utils.hasSearchEnd(search['processing'])  ): #
            #se actualiza en el PIPELINE
        #    yield item
        #else:#no existe el objeto luego se tiene que scrapear

            #BOLETINES
        if boletines or diarios:
            listurls = []
            enmiendas = []
            enmmocion = []
            if boletines:
                hasaprobdef = AmendmentFlow.hasAprobDef(boletines)
                for boletin in boletines:
                    text=boletin.xpath("text()").extract()
                    try:
                        serie= re.search('m. (.+?)-', text[0]).group(1)
                        haswordcongress = re.search('Congreso', text[0])
                    except:
                        serie = False
                        haswordcongress = False
                    url = boletin.xpath("a/@href").extract()
                    if (serie and haswordcongress):
                        listserie =[]
                        if Terms.isTextvalid(type,serie)\
                                and not AmendmentFlow.checkTypeAmendment(type=type,array=text,serie=serie)\
                                and not Utils.checkPreguntas(type)\
                                and not AmendmentFlow.checkTextodefinitivoarray(type=type,array=text,aprobdef=hasaprobdef):
                                #and not Utils.checkEnmiendainarray(text,serie)\
                                #and not Utils.checkTextodefinitivoarray(text) and not Utils.checkMocionEnmiendas(text,serie)\
                                #Si es valido el texto y no son enmiendas
                            listserie.append(serie)
                            listserie.append(url[0])
                            listurls.append(listserie)
                        elif AmendmentFlow.checkTypeAmendment(type=type,array=text,serie=serie):
                            if AmendmentFlow.getTypeAmendment(type) == "B":
                                enmiendas.append(url[0])
                            elif AmendmentFlow.getTypeAmendment(type) == "A":
                                enmmocion.append(url[0])
                        #buscando enmiendas
                        elif Utils.checkPreguntas(type) and Utils.checkContestacion(text):
                                ##Aqui van las respuestas
                            txtendurl = url[0]
                            responseitem = ResponseItem()
                            responseitem['reference'] = item['reference']
                            responseitem['title'] = item['title']
                            responseitem['author_deputies'] = []
                            responseitem['author_parliamentarygroups'] = []
                            responseitem['author_others'] = ["Gobierno"]
                            responseitem['url'] = item['url']
                            responseitem['content'] = []
                            responseitem['initiative_type'] = item ['initiative_type']
                            responseitem['initiative_type_alt'] = "Respuesta"
                            responseitem['place'] = item['place']
                            responseitem['processing'] = item['processing']
                            responseitem['created'] = item['created']
                            responseitem['ended'] = item['ended']
                            number = Utils.getnumber(txtendurl)
                            yield scrapy.Request(Utils.createUrl(response.url, txtendurl),
                                    errback=self.errback_httpbin,
                                    callback=self.responses, dont_filter=True,
                                    meta= {'responseitem':responseitem, 'text':"", 'linksenmiendas':None, 'isfirst':True, 'number':number}
                                         )

                        elif AmendmentFlow.checkTextodefinitivoarray(type=type,array=text,aprobdef=hasaprobdef):
                            #crea nuevo texto
                            if rtr: #si aprobado con modificaciones
                                if re.search('aprobado(.?)con(.?)modificaciones',rtr, re.IGNORECASE): # deberia ir todo los textos definitivos
                                    #se crea el nuevo objeto
                                    txtendurl = url[0]
                                    finishtextitem = FinishTextItem()
                                    finishtextitem['reference'] = item['reference']
                                    finishtextitem['title'] = item['title']
                                    # Inicio de caso especial para las 121 (proyecos de ley) en la que su autor siempre es Gobierno (author_other)
                                    finishtextitem['author_deputies'] = [] if item['initiative_type'] == "121" else item['author_deputies']
                                    finishtextitem['author_parliamentarygroups'] = [] if item['initiative_type'] == "121" else item['author_parliamentarygroups']
                                    finishtextitem['author_others'] = item['author_others']
                                    # Fin de caso especial
                                    finishtextitem['url'] = item['url']
                                    finishtextitem['content'] = []
                                    finishtextitem['initiative_type'] = item ['initiative_type']
                                    finishtextitem['initiative_type_alt'] = item['initiative_type_alt']+" Texto definitivo"
                                    finishtextitem['place'] = item['place']
                                    finishtextitem['processing'] = item['processing']
                                    finishtextitem['created'] = item['created']
                                    finishtextitem['ended'] = item['ended']
                                    yield scrapy.Request(Utils.createUrl(response.url, txtendurl),
                                                    errback=self.errback_httpbin,
                                                    callback=self.finishtext, dont_filter=True,
                                                    meta= {'fisnishitem':finishtextitem}
                                                         )
                #ENMIENDAS
            if enmiendas:
                for enm in enmiendas:
                    yield scrapy.Request(Utils.createUrl(response.url, enm),
                                         errback=self.errback_httpbin,
                                         callback=self.enmiendas, dont_filter=True,
                                            meta= {'item':item, 'text':"", 'linksenmiendas':None, 'isfirst':True}
                                         )
                #MOCION ENMIENDAS
            if enmmocion:
                for moen in enmmocion:
                        refmon = expt
                        number = Utils.getnumber(moen)
                        yield scrapy.Request(Utils.createUrl(response.url, moen),
                                                     errback=self.errback_httpbin,
                                                     callback=self.monenmiendas, dont_filter=True,
                                                     meta={'item': item, 'text': "", 'linksenmiendas': None, 'isfirst': True, 'pag':number,'reference':refmon}
                                                     )
                ##DIARIOS
            if diarios:
                if "DS" in Terms.getTypetext(type):
                    for diario in diarios:
                        text = diario.xpath("text()").extract()
                        url = diario.xpath("a/@href").extract()
                        if Utils.checkPreguntas(type):
                            ##Aqui van las respuestas
                            txtendurl = url[0]
                            responseitem = ResponseItem()
                            responseitem['reference'] = item['reference']
                            responseitem['title'] = item['title']
                            responseitem['author_deputies'] = []
                            responseitem['author_parliamentarygroups'] = []
                            responseitem['author_others'] = ["Gobierno"]
                            responseitem['url'] = item['url']
                            responseitem['content'] = []
                            responseitem['initiative_type'] = item ['initiative_type']
                            responseitem['initiative_type_alt'] = "Respuesta"
                            responseitem['place'] = item['place']
                            responseitem['processing'] = item['processing']
                            responseitem['created'] = item['created']
                            responseitem['ended'] = item['ended']
                            yield scrapy.Request(Utils.createUrl(response.url, txtendurl),
                                         errback=self.errback_httpbin,
                                         callback=self.responses, dont_filter=True,
                                            meta= {'responseitem':responseitem, 'text':"", 'linksenmiendas':None, 'isfirst':True,'number':None}
                                         )
                        else:
                            if re.search('Congreso', text[0]) :
                                listDS =[]
                                listDS.append("DS")
                                listDS.append(url[0])
                                listurls.append(listDS)
            if listurls:
                first_url = Utils.geturl(listurls[0])
                onlyserie = Utils.getserie(listurls[0])
                number = Utils.getnumber(first_url)
                Utils.delfirstelement(listurls)
                yield scrapy.Request(Utils.createUrl(response.url,first_url),
                                         errback=self.errback_httpbin,
                                         callback=self.recursiveletters, dont_filter = True,
                                         meta={'pag': number, 'item':item,'urls':listurls, 'isfirst': True, 'next':False,
                                               'serie': onlyserie })
            else:
                yield item
        else:
            yield item

    def extractplace(self, DS = None , com = None, type = None):
        try:
            if com:
                return com[0]
            elif DS and not re.search("DS", DS[0].xpath('./text()').extract()[0]) :
                return DS[0].xpath('./text()').extract()[0]
            elif re.search('pleno',type,re.IGNORECASE):
                return "Pleno"
            else:
                return ""
        except:
            pass

    def errback_httpbin(self, failure):

        self.logger.error(repr(failure))

        #if isinstance(failure.value, HttpError):
        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        #elif isinstance(failure.value, DNSLookupError):
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        #elif isinstance(failure.value, TimeoutError):
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def recursiveletters(self, response):
        number = response.meta['pag']
        item = response.meta['item']
        listurls = response.meta['urls']
        isfirst = response.meta['isfirst']
        itemserie = response.meta['serie']
        pages = Selector(response).xpath('//a/@name').extract()
        #si tiene paginador lo descartamos
        descarte = Selector(response).xpath('//p[@class="texto_completo"]')

        try:
            firstopage = re.search('gina(.+?)\)', pages[0]).group(1)
        except:
            firstopage= "1"


        if pages and not (str(int(firstopage)-1)==number) and not descarte:
            #aqui se busca
            try:
                if number:
                    haspage = [ch for ch in pages if re.search( 'gina' + number + '\)', ch)]
                else:
                    #debobuscar el numero
                     CheckSystem.systemlog("No encuentra el numero de la página " + response.url)


            except:
               CheckSystem.systemlog("El proceso de encontrar la pagina falla " + response.url)
        else:
            haspage = True

        if descarte:
            if itemserie=="DS":
                todosenlaces = descarte.xpath('a[contains(.,"arte")]/@href').extract()
                todosenlaces = list(set(todosenlaces))
                try:
                    first_url = todosenlaces[0]
                except:
                    CheckSystem.systemlog("No tiene mas url cuando si deberia tener " + response.url)
                Utils.delfirstelement(todosenlaces)
                #quitaelrepetido
                #self.delfirstelement(todosenlaces)



                fgr = self.searchDS(response, number,item['reference'],item["url"])
                yield scrapy.Request(Utils.createUrl(response.url, first_url), callback=self.recursiveDS,
                                     dont_filter=True, meta={'item': item,'allDS':todosenlaces, "texto":fgr})


            if listurls:
                first_url = Utils.geturl(listurls[0])
                onlyserie = Utils.getserie(listurls[0])

                number = Utils.getnumber(first_url)
                Utils.delfirstelement(listurls)
                yield scrapy.Request(Utils.createUrl(response.url,first_url),callback=self.recursiveletters,errback=self.errback_httpbin,
                                 dont_filter = True,  meta={'pag': number, 'item':item,'urls':listurls,
                                                             'isfirst':isfirst ,'serie':onlyserie})
            else:
                yield item



        elif isfirst and not descarte:
            if haspage:
                if not listurls:
                    if itemserie=="DS":
                        item['content'].append(self.searchDS(response, number,item['reference'],item["url"]))
                    else:
                        item['content'].append(self.searchpages(response, number, item['reference']))

                    yield item


                else:
                    if itemserie=="DS":
                        item['content'].append(self.searchDS(response, number,item['reference'],item["url"]))
                    else:
                        item['content'].append(self.searchpages(response, number, item['reference']))
                    first_url = Utils.geturl(listurls[0])
                    onlyserie = Utils.getserie(listurls[0])

                    number = Utils.getnumber(first_url)
                    Utils.delfirstelement(listurls)


                    yield scrapy.Request(Utils.createUrl(response.url,first_url), callback=self.recursiveletters,
                                         errback=self.errback_httpbin,
                                         dont_filter=True,
                                             meta={'pag': number, 'item': item, 'urls': listurls, 'isfirst': False,
                                                    'serie':onlyserie})
            #no tiene pagina
            else:
                if not listurls:

                    if itemserie=="DS":
                        item['content'].append(self.searchDS(response, number,item['reference'],item["url"]))
                    else:
                        item['content'].append(self.searchpages(response, number, item['reference']))
                    yield item
                else:
                    if itemserie=="DS":
                        item['content'].append(self.searchDS(response, number,item['reference'],item["url"]))
                    else:
                        item['content'].append(self.searchpages(response, number, item['reference']))
                    first_url = Utils.geturl(listurls[0])
                    onlyserie = Utils.getserie(listurls[0])

                    number = Utils.getnumber(first_url)
                    Utils.delfirstelement(listurls)

                    yield scrapy.Request(Utils.createUrl(response.url,first_url),
                                         errback=self.errback_httpbin,
                                         callback=self.recursiveletters, dont_filter=True,
                                             meta={'pag': number, 'item': item, 'urls': listurls, 'isfirst': "a",
                                                    'serie':onlyserie})


                    #este es el que devuelve el objeto, cuando no quedan urls
                    # Este es el esencial
        elif not listurls and not isfirst and not descarte:
                if haspage:
                    if itemserie=="DS":
                        item['content'].append(self.searchDS(response, number,item['reference'],item["url"]))
                    else:
                        item['content'].append(self.searchpages(response, number, item['reference']))
                    yield item
                else:
                    yield item


        elif not descarte:
            if itemserie == "DS":
                item['content'].append(self.searchDS(response, number, item['reference'], item["url"]))
            else:
                item['content'].append(self.searchpages(response, number, item['reference']))

            first_url = Utils.geturl(listurls[0])
            onlyserie = Utils.getserie(listurls[0])

            number = Utils.getnumber(first_url)
            Utils.delfirstelement(listurls)
            yield scrapy.Request(Utils.createUrl(response.url,first_url),
                                 errback=self.errback_httpbin,
                                 callback=self.recursiveletters,
                                 dont_filter = True,  meta={'pag': number, 'item':item,'urls':listurls,
                                                             'isfirst':False ,'serie':onlyserie})
        else:
            yield item

    def responses(self,response):
        #tambien debe tener recursion
        text = response.meta['text']
        item = response.meta['responseitem']
        links = response.meta['linksenmiendas']
        first = response.meta['isfirst']
        number = response.meta['number']
        try:
            text += Selector(response).xpath('//div[@class="texto_completo"]').extract()[0]

            if number:
                rsponsetext = self.extractbypagandref(text, item['reference'],number)
            else:
                rsponsetext = self.extractbyref(text, item['reference'])
        except:
            CheckSystem.systemlog("No tiene texto para 'RESPUESTAS' " + response.url + " Item url " + item['url'])


        try:
            if not rsponsetext and first:
                todosenlaces = Selector(response).xpath('//p[@class="texto_completo"]/a[contains(.,"arte")]/@href').extract()
                links=list(set(todosenlaces))
        except:
            links = False

        if rsponsetext:

            #timeprueba = datetime.datetime.now()


            #timeprueba = datetime.datetime.now() - timeprueba
            #print("********  %s " % timeprueba)
            item['content'] = []
            haspdf =re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.pdf', rsponsetext)
            if haspdf:
                item['content'].append(haspdf[0])
            else:
                item['content'].append(rsponsetext)
            Utils.removeHTMLtags(item['content'][0])
            yield item


        elif links and not rsponsetext:# aqui hay mas text
            first_url = links[0]
            Utils.delfirstelement(links)

            yield scrapy.Request(Utils.createUrl(response.url, first_url),
                                     errback=self.errback_httpbin,
                                     callback=self.responses, dont_filter=True,
                                        meta= {'responseitem':item, 'text':"", 'linksenmiendas':links, 'isfirst': False, 'number':number}
                                     )
        else:
            pass

    def extractresponse(self,text,ref):
        splittext = text.split("<br><br>")
        control = False
        result = []
        for line in splittext:
            if Utils.checkownRef(line, ref):
                control = True
            if not Utils.checkownRef(line, ref) and Utils.checkotherRef(line):
                control = False
            if control:
                result.append(line)
        return Utils.concatlist(result)


    def finishtext(self,response):
        finishitem = response.meta['fisnishitem']
        finishitem['content'] = []

        text = Selector(response).xpath('//div[@class="texto_completo"]').extract()[0]
        text= self.extractbyref(text=text,ref=finishitem['reference'])
        if text=="":
            try:
                text += Selector(response).xpath('//div[@class="texto_completo"]').extract()[0]
            except:
                CheckSystem.systemlog("No tiene texto para 'TEXTOFINAL' " + response.url + "ITEM URL "+finishitem['url'])

        finishitem['content'].append(Utils.removeHTMLtags(text))
        yield finishitem

    def enmiendas(self,response):
        #tmb debe tener recursion

        text = response.meta['text']
        item = response.meta['item']
        links = response.meta['linksenmiendas']
        first = response.meta['isfirst']

        try:
            if first:
                todosenlaces = Selector(response).xpath('//p[@class="texto_completo"]/a[contains(.,"arte")]/@href').extract()
                links=list(set(todosenlaces))
        except:
            links = False

        try:
            text += Selector(response).xpath('//div[@class="texto_completo"]').extract()[0]
        except:
            CheckSystem.systemlog("No tiene texto para 'ENMIENDAS' " + response.url)


        if not links :

            allenmiendas = self.amendmentFragment(response, text)
            for enmienda in allenmiendas:
                admendmentitem =  AmendmentItem()
                admendmentitem['title']= item['title']
                admendmentitem['reference'] = item['reference']
                admendmentitem['initiative_type'] = item['initiative_type']
                admendmentitem['initiative_type_alt'] = "Enmienda a "+item['initiative_type_alt']
                admendmentitem['place'] = item['place']
                admendmentitem['processing'] = item['processing']
                admendmentitem['created'] = item['created']
                admendmentitem['ended'] = item['ended']
                admendmentitem['url'] = item['url']
                splitenmienda = enmienda.split("<br><br>")

                index = None
                for line in splitenmienda:
                    if re.search('FIRMANTE',line):
                        index = splitenmienda.index(line)
                        break
                autors = []

                autors.append(splitenmienda[index + 1])

                autor = self.autorsAmendment(autors)
                typeaut = self.typeAutor(name=autor)

                admendmentitem['author_deputies'] = []
                admendmentitem['author_parliamentarygroups'] = []
                admendmentitem['author_others'] = []
                admendmentitem['content'] = []


                if typeaut is 'deputy':
                    admendmentitem['author_deputies'].append(autor)
                    try:
                        admendmentitem['author_parliamentarygroups'].append(self.getParliamentaryGroupFromDeputy(name=autor)['name'])
                    except:
                        CheckSystem.systemlog("Fallo en enmienda, no encuentra grupo parlamentario en la db" + response.url)
                elif typeaut is 'parliamentarygroup':
                    admendmentitem['author_parliamentarygroups'].append(self.getParliamentaryGroup(name=autor)['name'])
                elif typeaut is 'other':
                    admendmentitem['author_others'].append(autor)
                admendmentitem['content'].append(Utils.removeHTMLtags(Utils.concatlist(splitenmienda[index+2:])))

                yield admendmentitem




        else:# aqui hay mas text
            first_url = links[0]
            Utils.delfirstelement(links)
            yield scrapy.Request(Utils.createUrl(response.url, first_url),
                                     errback=self.errback_httpbin,
                                     callback=self.enmiendas, dont_filter=True,
                                        meta= {'item':item, 'text':text, 'linksenmiendas':links, 'isfirst':False}
                                     )

    def monenmiendas(self, response):
        #tmb debe tener recursion
        text = response.meta['text']
        item = response.meta['item']
        links = response.meta['linksenmiendas']
        first = response.meta['isfirst']
        refmon = response.meta['ref']
        number = response.meta['pag']

        try:
            if first:
                todosenlaces = Selector(response).xpath('//p[@class="texto_completo"]/a[contains(.,"arte")]/@href').extract()
                links=list(set(todosenlaces))
        except:
            links = False

        try:
            text += Selector(response).xpath('//div[@class="texto_completo"]').extract()[0]
        except:
            CheckSystem.systemlog("No tiene texto para 'ENMIENDAS' " + response.url)


        if not links :
            text = self.extractbypagandref(text, refmon, number)

            allenmiendas = self.monamendmentFragment(response, text)
            for enmienda in allenmiendas:
                admendmentitem =  AmendmentItem()
                admendmentitem['title']= item['title']
                admendmentitem['reference'] = item['reference']
                admendmentitem['initiative_type'] = item['initiative_type']
                admendmentitem['initiative_type_alt'] = "Enmienda a " + item['initiative_type_alt']
                admendmentitem['place'] = item['place']
                admendmentitem['processing'] = item['processing']
                admendmentitem['created'] = item['created']
                admendmentitem['ended'] = item['ended']
                admendmentitem['url'] = item['url']

                splitenmienda = enmienda.split("<br><br>")
                autors = []
                linesplit = ['Desconocido']

                for line in splitenmienda:
                    if re.search(u"Palacio del Congreso de los Diputados",line):
                        try:
                            limit = re.search(u"Palacio del Congreso de los Diputados(.*)[0-9]{4}.(.?)", line).group(2)
                        except:
                             CheckSystem.systemlog("No encuentra Palacio del Congreso en enmienda tipo A " + response.url)

                        linesplit = line.split(limit)[1:]


                autors = self.matchautorgroup(linesplit)
                admendmentitem['author_deputies'] = []
                admendmentitem['author_parliamentarygroups'] = []
                admendmentitem['author_others'] = []
                admendmentitem['content'] = []

                for autor in autors:
                    autor=autor['name']
                    typeaut = self.typeAutor(name=autor)

                    if typeaut is 'deputy':
                        admendmentitem['author_deputies'].append(autor)
                        try:
                            admendmentitem['author_parliamentarygroups'].append(self.getParliamentaryGroupFromDeputy(name=autor)['name'])
                        except:
                             CheckSystem.systemlog("Fallo en enmienda, no encuentra grupo en la db" + response.url)
                    elif typeaut is 'parliamentarygroup':
                        admendmentitem['author_parliamentarygroups'].append(self.getParliamentaryGroup(name=autor)['name'])
                    elif typeaut is 'other':
                        admendmentitem['author_others'].append(autor)

                admendmentitem['author_parliamentarygroups']= list(set(admendmentitem['author_parliamentarygroups']))
                admendmentitem['content'].append(Utils.removeHTMLtags(enmienda))

                yield admendmentitem




        else:# aqui hay mas text
            first_url = links[0]
            Utils.delfirstelement(links)
            yield scrapy.Request(Utils.createUrl(response.url, first_url),
                                 errback=self.errback_httpbin,
                                 callback=self.monenmiendas, dont_filter=True,
                                 meta={'item': item, 'text': "", 'linksenmiendas': None, 'isfirst': True, 'pag': number,
                                       'ref': refmon}
                                 )

    def matchautorgroup(self,lists):
        all = self.members+self.groups
        res = []
        for element in lists:
            subject = None
            max = 0
            for subj in all:
                ratio = fuzz.token_sort_ratio(element, subj['name'])
                if ratio > max:
                    subject = subj
                    max = ratio
            res.append(subject)
        return res

    def autorsAmendment(self,autors):
        #formatea si es un diputado de forma que se pueda buscar en la bd
        strip=autors[0].strip()
        typeaut = self.typeAutor(name=strip)
        if typeaut is not 'parliamentarygroup':
            max = 0
            member = None
            for memb in self.members:
                ratio = fuzz.token_sort_ratio(strip, memb['name'])
                if ratio > max:
                    member = memb
                    max = ratio
            return member['name']

        else:
            return strip

    def amendmentFragment(self, response, text):

        splittext = text.split("<br><br>")
        first = True
        currentnumber = '0'
        onlyenmienda = None
        allenmiendas= []
        for line in splittext:
            if re.search(u"ENMIENDA N(.+)M. (.+)",line):

                currentnumber = re.search(u"ENMIENDA N(.+)M. (.+)",line).group(2)

                if first:
                    first = False
                else:
                    allenmiendas.append(Utils.concatlist(onlyenmienda))
                onlyenmienda = []
                onlyenmienda.append(line)
            elif re.search(u"DE ENMIENDAS AL ARTICULADO",line) and not first: #el fist es para saber que es la coincidencia ultima
                allenmiendas.append(Utils.concatlist(onlyenmienda))
                onlyenmienda=[]
                break


            else:
                if currentnumber != '0':
                    onlyenmienda.append(line)
        if onlyenmienda: #si se queda el ultimo
            allenmiendas.append(Utils.concatlist(onlyenmienda))


        return allenmiendas

    def monamendmentFragment(self, response, text):

        splittext = text.split("<br><br>")
        first = True
        onlyenmienda = None
        allenmiendas = []
        for line in splittext:
            index = splittext.index(line)
            if re.search(u"Enmienda", line):

                if first:
                    first = False
                else:
                    allenmiendas.append(Utils.concatlist(onlyenmienda))
                onlyenmienda = []
                onlyenmienda.append(line)
            elif len(splittext) <= index :

                if re.search(u"Palacio del Congreso de los Diputados", #este es el que termina
                           line) and not (re.search(u"Enmienda", splittext[index+1])
                                or re.search(u"A la Mesa del Congreso de los Diputados",splittext[index+1])
                                                           or re.search(u"gina(.+?)\)",splittext[index+1]) ) and not first:
                    onlyenmienda.append(line)# el fist es para saber que es la coincidencia ultima
                    allenmiendas.append(Utils.concatlist(onlyenmienda))
                    onlyenmienda = []
                    break
            else:
                if onlyenmienda:
                    onlyenmienda.append(line)


        if onlyenmienda:  # si se queda el ultimo
            allenmiendas.append(Utils.concatlist(onlyenmienda))

        return allenmiendas

    def recursiveDS(self,response):
        text = response.meta['texto']
        item = response.meta['item']
        links = response.meta['allDS']
        text += self.searchDS(response, ref=item['reference'], name=item["url"])

        if not links:
            item['content'].append(text)
            yield item


        else:
            first_url = links[0]
            Utils.delfirstelement(links)
            yield scrapy.Request(Utils.createUrl(response.url, first_url), callback=self.recursiveDS,
                             dont_filter=True, meta={'item': item, 'allDS': links, "texto": text})

    def searchDS(self,  response , number = None ,ref = None , name = None):
        try:
            text = Selector(response).xpath('//div[@class="texto_completo"]').extract()
            return Utils.removeForDS(text[0])
        except:
            return "URL rota"

    def searchpages(self,response, number, expt):

        pages = Selector(response).xpath('//a/@name').extract()
        haspage = [ch for ch in pages if re.search('gina' + number + '\)', ch)]
        if haspage:
            publications = self.extracttext(response, number,expt)
            return publications
        else:
            if number=="1":
                return self.extracttext(response, number,expt)
            else:
                try:
                    return "Error  "+number + " URL: "+response.url
                except:
                    return "ERROR"

    def extracttext(self, response, number, ref):
        textfragment = self.fragmenttxt(response,number)
        res = ""
        #Es el texto entero y no hay que fragmentar
        if not Utils.checkownRef(textfragment,ref):
            return Utils.removeHTMLtags(textfragment)

        texto = self.extractbyref(textfragment,ref,number)
        pages = Selector(response).xpath('//a/@name').extract()

        #para empezar desde el indice
        #bbusca mas texto
        hasfirsttext = False
        if Utils.isDiferentFirstTime(textfragment,ref):
            hasfirsttext=True
        if not hasfirsttext:
            pages = Utils.convertPagToNum(pages)
            try:
                index = pages.index(number)
            except:
                index=0
            for page in pages[index:]:
                if int(page) > int(number):
                    textfragment = self.fragmenttxt(response, page)
                    texto += self.extractother(textfragment, ref)
                    #si encuentra el otro rompe bucle
                    if Utils.checkotherRefandnotOwn(textfragment,ref):
                        break
        res = Utils.removeHTMLtags(texto)

        return res

    def extractbyref(self,text, ref, number=None):
        splittext = text.split("<br><br>")
        control = False
        result = []
        for line in splittext:
            if Utils.checkownRef(line,ref):
                control = True
            if not Utils.checkownRef(line, ref) and Utils.checkotherRef(line):
                control = False
            if control:
                result.append(line)
        return Utils.concatlist(result)

    def extractbypagandref(self, text, ref, number):
        #aqui ya se tiene el texto acotado por ref
        splittext = text.split("<br><br>")
        controlpag = False
        controlref = False
        result = []
        for line in splittext:
            if Utils.checkPage(line,number):
                controlpag= True
            elif controlpag and Utils.checkownRef(line, ref) and not controlref:

                controlref = True
                result.append(line)
            elif controlpag and controlref and not (Utils.checkotherRef(line) and not Utils.checkownRef(line, ref)):
                result.append(line)
            elif controlpag and controlref and (Utils.checkotherRef(line) and not Utils.checkownRef(line, ref)):
                break
        return Utils.concatlist(result)

    def extractother(self,text,ref):
        splittext = text.split("<br><br>")
        control = True
        result = []


        for line in splittext:
            if control:
                result.append(line)
            if not Utils.checkownRef(line, ref) and Utils.checkotherRef(line):
                control = False



        return Utils.concatlist(result)

    def fragmenttxt(self, response,number):
        pages = Selector(response).xpath('//p/a/@name').extract()
        text = Selector(response).xpath('//div[@class="texto_completo"]').extract()
        result = []
        control = False


        try:
            firstopage = Utils.getnumber(pages[0])
        except:
            firstopage= "1"
            control = True

        # selecciona del texto solo la pagina que nos resulta útil
        splittext = text[0].split("<br><br>")
        for i in splittext:
            if Utils.checkPage(i,number):
                control = True
                continue
            elif int(number) < int(firstopage):
                control = True
            if control  and Utils.checkPage(i,str(int(number)+1)):
                break
            if control:
                result.append(i)


        return Utils.concatlist(result)


    def getDeputy(self,  name=None):
        for member in self.members:
            if name == member['name']:
                return member

        return None


    def getParliamentaryGroupFromDeputy(self, name=None):
        deputy = self.getDeputy(name)
        return self.getParliamentaryGroup(name=deputy['parliamentarygroup'])


    def getParliamentaryGroup(self, name=None):
        # sebusca por acronimo
        acronimo = None
        if re.search("la izquierda plural", name, re.IGNORECASE) \
                or re.search("GIP", name, re.IGNORECASE):
            acronimo = u'GIP'
        elif re.search("popular", name, re.IGNORECASE) \
                or re.search("GP", name, re.IGNORECASE):
            acronimo = u'GP'
        elif re.search("vasco", name, re.IGNORECASE) \
                or re.search("EAJ-PNV", name, re.IGNORECASE):
            acronimo = u'GV (EAJ-PNV)'
        elif re.search("socialista", name, re.IGNORECASE) \
                or re.search("GS", name, re.IGNORECASE):
            acronimo = u'GS'
        elif re.search("mixto", name, re.IGNORECASE) \
                or re.search("GMx", name, re.IGNORECASE):
            acronimo = u'GMx'
        elif re.search("converg", name, re.IGNORECASE) \
                or re.search("GC-CiU", name, re.IGNORECASE):
            acronimo = u'GC-CiU'
        elif re.search("progreso", name, re.IGNORECASE) \
                or re.search("GUPyD", name, re.IGNORECASE):
            acronimo = u'GUPyD'
        elif re.search("ciudadanos", name, re.IGNORECASE) \
                 or re.search("GCs", name, re.IGNORECASE):
            acronimo = u'GCs'
        elif re.search("republicana", name, re.IGNORECASE) \
                or re.search("GER", name, re.IGNORECASE):
            acronimo = u'GER'
        elif re.search("podemos", name, re.IGNORECASE) \
                or re.search("GCUP-EC-EM", name, re.IGNORECASE):
            acronimo = u'GCUP-EC-EM'

        for group in self.groups:
            if acronimo == group['shortname']:
                return group

        return None


    def typeAutor(self, name):
        if self.getDeputy(name=name):
            return 'deputy'
        elif self.getParliamentaryGroup(name=name):
            return 'parliamentarygroup'
        else:
            return 'other'
