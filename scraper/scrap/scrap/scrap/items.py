# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field


class InitiativeItem(Item):
    ref = Field()
    titulo = Field()
    autor_diputado = Field()
    autor_grupo = Field()
    autor_otro = Field()
    url = Field()
    contenido = Field()
    tipo = Field()
    tipotexto = Field()
    tramitacion = Field()
    fecha = Field()
    fechafin = Field()
    lugar = Field()


class AmendmentItem(Item):
    ref = Field()
    titulo = Field()
    autor_diputado = Field()
    autor_grupo = Field()
    autor_otro = Field()
    url = Field()
    contenido = Field()
    tipo = Field()
    tipotexto = Field()
    tramitacion = Field()
    fecha = Field()
    fechafin = Field()
    lugar = Field()

class FinishTextItem(Item):
    ref = Field()
    titulo = Field()
    autor_diputado = Field()
    autor_grupo = Field()
    autor_otro = Field()
    url = Field()
    contenido = Field()
    tipo = Field()
    tipotexto = Field()
    tramitacion = Field()
    restramitacion = Field()
    fecha = Field()
    fechafin = Field()
    lugar = Field()

class ResponseItem(Item):
    ref = Field()
    titulo = Field()
    autor_diputado = Field()
    autor_grupo = Field()
    autor_otro = Field()
    url = Field()
    contenido = Field()
    tipo = Field()
    tipotexto = Field()
    tramitacion = Field()
    restramitacion = Field()
    fecha = Field()
    fechafin = Field()
    lugar = Field()

class MemberItem(Item):
    nombre = Field()
    url = Field()
    grupo = Field()
    correo = Field()
    web = Field()
    twitter= Field()
    fecha_alta = Field()
    fecha_baja = Field()
    imagen = Field()
    tipi=Field()
    activo=Field()

