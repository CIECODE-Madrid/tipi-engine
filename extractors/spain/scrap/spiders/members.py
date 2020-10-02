from urllib.parse import urlparse
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector, Selector
from scrapy.item import Item, Field
import re
from dateutil.parser import parse

from database.congreso import Congress
from extractors.config import ID_LEGISLATURA
from scrap.items import MemberItem


class MemberSpider(CrawlSpider):
    name = 'members'
    allowed_domains = ['congreso.es', ]
    start_urls = [  'http://www.congreso.es/portal/page/portal/Congreso'
                        '/Congreso/Diputados?_piref73_1333056_73_1333049_13'
                        '33049.next_page=/wc/menuAbecedarioInicio&tipoBusqu'
                        'eda=completo&idLegislatura={}'.format(ID_LEGISLATURA),
                    'http://www.congreso.es/portal/page/portal/Congreso/Congreso/Diputados/BajasLegAct']

    rules = []
    rules.append(
            Rule(LinkExtractor(
                allow=['fichaDiputado\?idDiputado=\d+&idLegislatura={}'.format(ID_LEGISLATURA)], unique=True),
                       callback='parse_member'))
    rules.append(
            Rule(LinkExtractor(
                allow=['busquedaAlfabeticaDiputados&paginaActual=\d+&idLeg'
                       'islatura={}'
                       '&tipoBusqueda=completo'.format(ID_LEGISLATURA)], unique=True), follow=True))
    rules.append(
            Rule(LinkExtractor(
                allow=['diputadosBajaLegActual&paginaActual=\d']
                    , unique=True), follow=True))

    def text_cleaner(self,text):
        regex = re.compile(r'[\n\r\t]')
        res = regex.sub(" ",text)
        res = res.replace("<li>","").replace("</li>","").replace("  ","").replace(u'\xa0', u' ').strip()
        return res



    def parse_member(self, response):


        # extract full name of member
        names = Selector(response).xpath('//div[@class="nombre_dip"]/text()').extract()
        # extra text like member's state
        curriculum = Selector(response).xpath('//div[@class="texto_dip"]/ul/li/div[@class="dip'
                              '_rojo"]')

        # email, twitter ....
        extra_data = Selector(response).xpath('//div[@class="webperso_dip"]/div/a/@href')
        avatar = Selector(response).xpath('//div[@id="datos_diputado"]/p[@class="logo_g'
                          'rupo"]/img[@name="foto"]/@src').extract()
        constituency = Selector(response).xpath('//div[@class="texto_dip"]/ul/li[1]/div[1][@class="dip_rojo"]').css('::text').extract()[0].strip().split()[2]
        resources = Selector(response).xpath("//ul/li[@class='regact_dip']").css('a::attr(href)').extract()
        congress_position = Selector(response).xpath("//p[@class='pos_hemiciclo']/img").css('::attr(src)').extract()
        public_charges = Selector(response).xpath('(//div[@class = "listado_1"])[1]/ul/li').extract()
        birthday = Selector(response).xpath('((//div[@class="texto_dip"])[2]/ul/li)[1]').extract()
        legislatures = Selector(response).xpath('((//div[@class="texto_dip"])[2]/ul/li)[2]').extract()
        bio = Selector(response).xpath('((//div[@class="texto_dip"])[2]/ul/li)[3]').extract()
        social_networks = Selector(response).xpath('//div[@class="webperso_dip"]/div[@class="webperso_dip_imagen"]/a/@href')
        party_logo = Selector(response).xpath('(//p[@class = "logo_grupo"])[2]/a/img/@src').extract()
        item = MemberItem()
        
        item['url'] = response.url
        item['name'] = ""
        item['image'] = ""
        item['parliamentarygroup'] = ""
        item['start_date'] = ""
        item['end_date'] = ""
        item['web'] = ""
        item['email'] = ""
        item['twitter'] = ""
        item['facebook'] = ""
        #item['instagram'] = ""
        item['active'] = True
        item['constituency'] = ""
        #item['activity_resource'] = ""
        #item['assets_resource'] = ""
        item['public_charges'] = []
        item['birthday'] = ""
        #item['legislatures'] = ""
        item['bio']=[]
        #item['party_logo']=""
        item['extra']={}
        item['extra']['activity_resource']=""
        item['extra']['assets_resource']=""
        item['extra']['legislatures']=""
        item['extra']['party_logo']=""
        

        if names:
            second_name, name = names[0].split(',')
            item['name'] = second_name.strip()+", "+name.strip()
            if constituency:
                item['constituency'] = constituency
            if len(resources)>0:
                item['extra']['activity_resource'] = 'http://www.congreso.es' + resources[0]
            if len(resources)>1:
                item['extra']['assets_resource'] = 'http://www.congreso.es' + resources[1]
            if avatar:
                item['image'] = 'http://www.congreso.es' + avatar[0]
            if public_charges: 
                resu = []
                for s in public_charges:
                    res = self.text_cleaner(s)
                    ini = res[:res.find('<a')] 
                    fin = res[res.find('class')+9:res.find('</a')]
                    string = ini + fin
                    resu.append(string)
                item['public_charges'] = resu
            if birthday:
                resu = []
                for s in birthday:
                    res = self.text_cleaner(s)
                    resu.append(res)
                item['birthday'] = resu[0]
            if legislatures:
                resu = []
                for s in legislatures:
                    res = self.text_cleaner(s)
                    resu.append(res)
                item['extra']['legislatures']= resu[0]
            if bio:
                resu = []
                for s in bio:
                    res = self.text_cleaner(s)
                    resu = res.split('<br>')
                item['bio'] = resu
            if len(social_networks)>0:
                for net in social_networks:
                    twitter = net.re('[http|https]*://(?:twitter.com)/[\w]*')
                    if twitter:
                        item['twitter'] = twitter[0]
                    facebook = net.re('[http|https]*://(?:www.facebook.com)/[\w]*')
                    if facebook:
                        item['facebook'] = facebook[0]
                    #instagram = net.re('[http|https]*://(?:www.instagram.com)/[\w]*')
                    #if instagram:
                     #   item['instagram'] = instagram[0]
            if party_logo:
                item['extra']['party_logo'] = "http://congreso.es" + party_logo[0]

            if curriculum:

                group = curriculum.xpath('a/text()')

                if group:
                    # url is in list, extract it
                    item['parliamentarygroup'] = re.search('\( (.*?) \)', group.extract()[0]).group(1).strip()
                    #item['party_logo'] = 'http://www.congreso.es' +Selector(response).xpath('//div[@id="datos_diputado"]/p[@cl'
                    #                       'ass="logo_grupo"]/a/img/@src').\
                    #                       extract()[0] #logo de partido
                    #item['party_name'] = Selector(response).xpath('//div[@id="datos_diputado"]/p[@clas'
                    #                      's="nombre_grupo"]/text()').extract()[0] #nombre partido


                    # add dates of inscription and termination
                    ins_date = curriculum.re('(?i)(?<=fecha alta:)[\s]*[\d\/]*')
                    if ins_date:
                        item['start_date'] = parse(ins_date[0], dayfirst=True)

                    term_date = curriculum.re('(?i)(?<=baja el)[\s]*[\d\/]*')
                    if term_date:
                        item['end_date'] = parse(term_date[0], dayfirst=True)
                        item['active'] = False

            if extra_data:
                web_data = Selector(response).xpath('//div[@class="webperso_dip"]/div[@class="'
                                    'webperso_dip_parte"]/a/@href')
                if web_data:
                    web = web_data.re('[http|https]*://.*')
                    if web:
                        item['web'] = web[0]
                email = extra_data.re('mailto:[\w.-_]*@[\w.-_]*')
                if email:
                    item['email'] = email[0].replace('mailto:', '')
                #twitter = extra_data.re('[http|https]*://(?:twitter.com)/[\w]*')
                #if twitter:
                 #   item['twitter'] = twitter[0]
        congress = Congress()
        search = congress.getDeputy(name=item['name'])
        if not search:
            congress.updateorinsertDeputy(type="insert",item=item)
        else:
            congress.updateorinsertDeputy(type="update", item=item)
        return item
