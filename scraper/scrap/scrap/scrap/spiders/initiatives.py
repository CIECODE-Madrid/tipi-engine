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
        self.members = self.congress.searchAll("diputados")
        self.groups = self.congress.searchAll("grupos")
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

            if Blacklist.getElement(initiative_url):
                if not Blacklist.getElement(initiative_url):
                    yield scrapy.Request(initiative_url,errback=self.errback_httpbin,
                                         callback=self.oneinitiative, meta = {'type':type})
            else:
                yield scrapy.Request(initiative_url,errback=self.errback_httpbin,
                                     callback=self.oneinitiative, meta = {'type':type})

    def oneinitiative(self,response):
        type = response.meta['type'] #tipotexto
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
        item['ref'] = expt
        item['titulo'] = Utils.clearTitle(title)
        item['url'] = response.url
        ##control autor
        item['autor_diputado'] = []
        item['autor_grupo'] = []
        item['autor_otro'] = []
        for oneaut in listautors:
            typeaut = self.typeAutor(name=oneaut)
            if typeaut is 'diputado':
                item['autor_diputado'].append(oneaut)
                try:
                    item['autor_grupo'].append(self.getGroupfrommember(name=oneaut)['nombre'])
                except:
                    CheckSystem.systemlog("Fallo en enmienda, no encuentra grupo parlamentario en la db" + response.url)
            elif typeaut is 'grupo':
                item['autor_grupo'].append(self.getGroup(name=oneaut)['nombre'])
            elif typeaut is 'otro':
                item['autor_otro'].append(oneaut)
        #si hubiera varios autores del mismo grupo
        item['autor_grupo']= list(set(item['autor_grupo']))
        item['tipotexto'] = type
        item['tipo'] = re.search('[0-9]{3}', expt).group(0)

        item["contenido"]=[]

        #si hay comisiones meter la comision(es donde se habla de las inicitativas
        if comision:
            comision = comision.xpath("./a/b/text()").extract()

        item["lugar"] = self.extractplace(DS = diarios, com = comision , type = type)
        item["tramitacion"] = ""

        item['fecha'] = ""
        item['fechafin'] = "En trámite"
        try:
            if presentado:
                #se obtiene la fecha

                fechainicio = re.search('([0-9]{2}\/[0-9]{2}\/[0-9]{4}),', presentado[0]).group(1).strip() #se obtiene la fecha
                item['fecha'] = Utils.getDateobject(fechainicio)
                #control de fecha final
                if re.search('calificado el ([0-9]{2}\/[0-9]{2}\/[0-9]{4}) ', presentado[0]):
                    item['fechafin'] = Utils.getDateobject(re.search('calificado el ([0-9]{2}\/[0-9]{2}\/[0-9]{4}) ', presentado[0]).group(1))

            else:
                item['fecha'] ="Fecha no encontrada"

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
            item["tramitacion"] = Utils.removeHTMLtags(rtr)
        elif tr:
            item["tramitacion"] = Utils.removeHTMLtags(tr)
        else:
            item["tramitacion"] = "Desconocida"

        #saber si se ha actualizado
        #search = self.congress.getInitiative(collection="iniciativas",ref=item['ref'],tipotexto=item['tipotexto'],titulo=item['titulo'])
        #if search and ((not Utils.checkTypewithAmendments(type) and not Utils.checkPreguntas(type)) or  Utils.hasSearchEnd(search["tramitacion"])  ): #
            #se actualiza en el PIPELINE
        #    yield item
        #else:#no existe el objeto luego se tiene que scrapear
            #BOLETINES
        if boletines or diarios:
            listurls=[]
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
                            responseitem['ref'] = item['ref']
                            responseitem['titulo'] = item['titulo']
                            responseitem['autor_diputado'] = []
                            responseitem['autor_grupo'] = []
                            responseitem['autor_otro'] = ["Gobierno"]
                            responseitem['url'] = item['url']
                            responseitem['contenido'] = []
                            responseitem['tipo'] = item ['tipo']
                            responseitem['tramitacion'] = item['tramitacion']
                            responseitem['fecha'] = item['fecha']
                            responseitem['fechafin'] = item['fechafin']
                            responseitem['lugar'] = item['lugar']
                            responseitem['tipotexto'] = "Respuesta"
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
                                    finishtextitem['ref'] = item['ref']
                                    finishtextitem['titulo'] = item['titulo']
                                    # Inicio de caso especial para las 121 (proyecos de ley) en la que su autor siempre es Gobierno (autor_otro)
                                    finishtextitem['autor_diputado'] = [] if item['tipo'] == "121" else item['autor_diputado']
                                    finishtextitem['autor_grupo'] = [] if item['tipo'] == "121" else item['autor_grupo']
                                    finishtextitem['autor_otro'] = item['autor_otro']
                                    # Fin de caso especial
                                    finishtextitem['url'] = item['url']
                                    finishtextitem['contenido'] = []
                                    finishtextitem['tipo'] = item ['tipo']
                                    finishtextitem['tramitacion'] = item['tramitacion']
                                    finishtextitem['fecha'] = item['fecha']
                                    finishtextitem['fechafin'] = item['fechafin']
                                    finishtextitem['lugar'] = item['lugar']
                                    finishtextitem['tipotexto'] = item['tipotexto']+" Texto definitivo"
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
                                                     meta={'item': item, 'text': "", 'linksenmiendas': None, 'isfirst': True, 'pag':number,'ref':refmon}
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
                            responseitem['ref'] = item['ref']
                            responseitem['titulo'] = item['titulo']
                            responseitem['autor_diputado'] = []
                            responseitem['autor_grupo'] = []
                            responseitem['autor_otro'] = ["Gobierno"]
                            responseitem['url'] = item['url']
                            responseitem['contenido'] = []
                            responseitem['tipo'] = item ['tipo']
                            responseitem['tramitacion'] = item['tramitacion']
                            responseitem['fecha'] = item['fecha']
                            responseitem['fechafin'] = item['fechafin']
                            responseitem['lugar'] = item['lugar']
                            responseitem['tipotexto'] = "Respuesta"
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



                fgr = self.searchDS(response, number,item["ref"],item["url"])
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
                        item["contenido"].append(self.searchDS(response, number,item["ref"],item["url"]))
                    else:
                        item["contenido"].append(self.searchpages(response, number, item["ref"]))

                    yield item


                else:
                    if itemserie=="DS":
                        item["contenido"].append(self.searchDS(response, number,item["ref"],item["url"]))
                    else:
                        item["contenido"].append(self.searchpages(response, number, item["ref"]))
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
                        item["contenido"].append(self.searchDS(response, number,item["ref"],item["url"]))
                    else:
                        item["contenido"].append(self.searchpages(response, number, item["ref"]))
                    yield item
                else:
                    if itemserie=="DS":
                        item["contenido"].append(self.searchDS(response, number,item["ref"],item["url"]))
                    else:
                        item["contenido"].append(self.searchpages(response, number, item["ref"]))
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
                        item["contenido"].append(self.searchDS(response, number,item["ref"],item["url"]))
                    else:
                        item["contenido"].append(self.searchpages(response, number, item["ref"]))
                    yield item
                else:
                    yield item


        elif not descarte:
            if itemserie == "DS":
                item["contenido"].append(self.searchDS(response, number, item["ref"], item["url"]))
            else:
                item["contenido"].append(self.searchpages(response, number, item["ref"]))

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
                rsponsetext = self.extractbypagandref(text, item['ref'],number)
            else:
                rsponsetext = self.extractbyref(text, item['ref'])
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
            item["contenido"] = []
            haspdf =re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.pdf', rsponsetext)
            if haspdf:
                item["contenido"].append(haspdf[0])
            else:
                item["contenido"].append(rsponsetext)
            Utils.removeHTMLtags(item['contenido'][0])
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
        finishitem['contenido'] = []

        text = Selector(response).xpath('//div[@class="texto_completo"]').extract()[0]
        text= self.extractbyref(text=text,ref=finishitem['ref'])
        if text=="":
            try:
                text += Selector(response).xpath('//div[@class="texto_completo"]').extract()[0]
            except:
                CheckSystem.systemlog("No tiene texto para 'TEXTOFINAL' " + response.url + "ITEM URL "+finishitem['url'])

        finishitem['contenido'].append(Utils.removeHTMLtags(text))
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
                admendmentitem['titulo']= item['titulo']
                admendmentitem['tipo'] = item['tipo']
                admendmentitem['tipotexto'] = "Enmienda a "+item['tipotexto']
                admendmentitem['ref'] = item['ref']
                admendmentitem['url'] = item['url']
                admendmentitem['lugar'] = item['lugar']
                admendmentitem['tramitacion'] = item['tramitacion']
                admendmentitem['fecha'] = item['fecha']
                admendmentitem['fechafin'] = item['fechafin']
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

                admendmentitem['autor_diputado'] = []
                admendmentitem['autor_grupo'] = []
                admendmentitem['autor_otro'] = []
                admendmentitem['contenido'] = []


                if typeaut is 'diputado':
                    admendmentitem['autor_diputado'].append(autor)
                    try:
                        admendmentitem['autor_grupo'].append(self.getGroupfrommember(name=autor)['nombre'])
                    except:
                        CheckSystem.systemlog("Fallo en enmienda, no encuentra grupo parlamentario en la db" + response.url)
                elif typeaut is 'grupo':
                    admendmentitem['autor_grupo'].append(self.getGroup(name=autor)['nombre'])
                elif typeaut is 'otro':
                    admendmentitem['autor_otro'].append(autor)
                admendmentitem['contenido'].append(Utils.removeHTMLtags(Utils.concatlist(splitenmienda[index+2:])))

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
                admendmentitem['titulo']= item['titulo']
                admendmentitem['tipo'] = item['tipo']
                admendmentitem['tipotexto'] = "Enmienda a " + item['tipotexto']
                admendmentitem['ref'] = item['ref']
                admendmentitem['url'] = item['url']
                admendmentitem['lugar'] = item['lugar']
                admendmentitem['tramitacion'] = item['tramitacion']
                admendmentitem['fecha'] = item['fecha']
                admendmentitem['fechafin'] = item['fechafin']

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
                admendmentitem['autor_diputado'] = []
                admendmentitem['autor_grupo'] = []
                admendmentitem['autor_otro'] = []
                admendmentitem['contenido'] = []

                for autor in autors:
                    autor=autor['nombre']
                    typeaut = self.typeAutor(name=autor)

                    if typeaut is 'diputado':
                        admendmentitem['autor_diputado'].append(autor)
                        try:
                            admendmentitem['autor_grupo'].append(self.getGroupfrommember(name=autor)['nombre'])
                        except:
                             CheckSystem.systemlog("Fallo en enmienda, no encuentra grupo en la db" + response.url)
                    elif typeaut is 'grupo':
                        admendmentitem['autor_grupo'].append(self.getGroup(name=autor)['nombre'])
                    elif typeaut is 'otro':
                        admendmentitem['autor_otro'].append(autor)

                admendmentitem['autor_grupo']= list(set(admendmentitem['autor_grupo']))
                admendmentitem['contenido'].append(Utils.removeHTMLtags(enmienda))

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
            member = None
            max = 0
            for memb in all:
                ratio = fuzz.token_sort_ratio(element, memb['nombre'])
                if ratio > max:
                    member = memb
                    max = ratio
            res.append(member)
        return res

    def autorsAmendment(self,autors):
        #formatea si es un diputado de forma que se pueda buscar en la bd
        strip=autors[0].strip()
        typeaut = self.typeAutor(name=strip)
        if typeaut is not 'grupo':
            max = 0
            member = None
            for memb in self.members:
                ratio = fuzz.token_sort_ratio(strip, memb['nombre'])
                if ratio > max:
                    member = memb
                    max = ratio
            return member['nombre']

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
        text += self.searchDS(response, ref=item["ref"], name=item["url"])

        if not links:
            item["contenido"].append(text)
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

    def extractbyref(self,text, ref ,number=None):
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


    def getMember(self,  name=None):
        for member in self.members:
            if name == member['nombre']:
                return member

        return None


    def getGroupfrommember(self, name=None):
        search = self.getMember(name)
        return self.getGroup(name=search['grupo'])


    def getGroup(self, name=None):
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
            if acronimo == group['acronimo']:
                return group

        return None


    def typeAutor(self, name):
        if self.getMember(name=name):
            return "diputado"
        elif self.getGroup(name=name):
            return "grupo"
        else:
            return "otro"
