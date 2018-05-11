import urlparse


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector, Selector
from scrapy.item import Item, Field
import pdb
import re
from dateutil.parser import parse

from database.congreso import Congress

from scrap.items import MemberItem


class MemberSpider(CrawlSpider):
    name = 'members'
    allowed_domains = ['congreso.es', ]
    start_urls = ['http://www.congreso.es/portal/page/portal/Congreso'
                           '/Congreso/Diputados?_piref73_1333056_73_1333049_13'
                           '33049.next_page=/wc/menuAbecedarioInicio&tipoBusqu'
                           'eda=completo&idLegislatura=12' ]

    rules = []
    rules.append(
            Rule(LinkExtractor(
                allow=['fichaDiputado\?idDiputado=\d+&idLegislatura=12'], unique=True),
                       callback='parse_member'))
    rules.append(
            Rule(LinkExtractor(
                allow=['busquedaAlfabeticaDiputados&paginaActual=\d+&idLeg'
                       'islatura=12'
                       '&tipoBusqueda=completo'], unique=True), follow=True))







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
        item['active'] = True

        if names:
            second_name, name = names[0].split(',')
            item['name'] = second_name.strip()+", "+name.strip()
            if avatar:
                item['image'] = 'http://www.congreso.es' + avatar[0]
            if curriculum:

                group = curriculum.xpath('a/text()')

                #pdb.set_trace()
                if group:
                    # url is in list, extract it
                    item['parliamentarygroup'] = re.search('\((.*?)\)', group.extract()[0]).group(1).strip()
                    #item['party_logo'] = 'http://www.congreso.es' +Selector(response).xpath('//div[@id="datos_diputado"]/p[@cl'
                    #                       'ass="logo_grupo"]/a/img/@src').\
                    #                       extract()[0] #logo de partido
                    #item['party_name'] = Selector(response).xpath('//div[@id="datos_diputado"]/p[@clas'
                    #                      's="nombre_grupo"]/text()').extract()[0] #nombre partido


                    # add dates of inscription and termination
                    ins_date = curriculum.re('(?i)(?<=fecha alta:)[\s]*[\d\/]*')
                    if ins_date:
                        item['start_date'] = parse\
                                                   (ins_date[0], dayfirst=True)
                    term_date = curriculum.re('(?i)(?<=caus\xf3 baja el)[\s]*['
                                             '\d\/]*')
                    if term_date:
                        item['end_date'] = parse\
                                                 (term_date[0], dayfirst=True)
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
                twitter = extra_data.re('[http|https]*://(?:twitter.com)/[\w]*')
                if twitter:
                    item['twitter'] = twitter[0]
        congress = Congress()
        search = congress.getDeputy(name=item['name'])
        if not search:
            congress.updateorinsertDeputy(type="insert",item=item)
        else:
            congress.updateorinsertDeputy(type="update", item=item)
        return item
