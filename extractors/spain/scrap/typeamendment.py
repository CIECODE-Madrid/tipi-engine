# -*- coding: utf-8 -*-
import re
import pdb

dicc = {

    #primera posicion: tipo de Boletin donde se encuentran
    #Segunda posicion: texto de enmiendas. ARRAY, el primero tiene mas prioridad. PD. Son usados por regexps
    #tercera posicion: tipo de enmiendas (A es el que no tiene numero y b el que si)
    #cuarta posicion: texto de texto final ARRAY, el primero tiene mas prioridad - esta ahora mismo no tiene mucho sentido porq solo se prueba aprobacion
    #NOTA: los textos tengan aprobacion definitivas, se miran en la funcion. No esta en la array


     u'Proposición no de Ley ante el Pleno':["D", ["Enmiendas"], "B", ["aprobaci(.+?)n(.*?)por(.*?)el(.*?)pleno"]],
     u'Proposición no de Ley en Comisión': ["D", ["Enmiendas"],"B", ["aprobaci(.+?)n(.*?)por(.*?)el(.*?)pleno"]],
     u'Iniciativa legislativa popular':["B",["dice de enmiendas"],"B", ["aprobaci(.+?)n"]],
     u'Proposición de ley de Grupos Parlamentarios del Congreso':["B",["Enmiendas"],"B",["aprobaci(.+?)n"]],
     u'Proposición de ley de Diputados':["B",["Enmiendas"],"B",["aprobaci(.+?)n"]],
     u'Proposición de ley de Comunidades y Ciudades Autónomas':["B",["Enmiendas"],"B",["aprobaci(.+?)n"]],
     u'Proposición de ley del Senado':["B",["Enmiendas"],"B",["aprobaci(.+?)n"]],
     u'Proyecto de ley': ["A",["dice de enmiendas","Enmiendas"],"B",["aprobaci(.+?)n"]],
     u'Proposición de reforma del Reglamento del Congreso':["B",["Enmiendas"],"B",["aprobaci(.+?)n"]],

}



class AmendmentFlow(object):
    @staticmethod
    def getDict():
        return dicc
    @staticmethod
    def getTypeBol(key):
        return AmendmentFlow.getDict()[key][0]

    @staticmethod
    def getTextAmendment(key):
        return AmendmentFlow.getDict()[key][1]

    @staticmethod
    def getTypeAmendment(key):
        return AmendmentFlow.getDict()[key][2]

    @staticmethod
    def getFinishText(key):
        return AmendmentFlow.getDict()[key][3]

    @staticmethod
    def getAllinfo(key):
        """
        :param key: key dicc
        :rtype: array
        :return:  Return all type info
        """
        return AmendmentFlow.getDict()[key]



    @staticmethod
    def getKeys():
        return AmendmentFlow.getDict().keys()


    @staticmethod
    def getValues():
        return AmendmentFlow.getDict().values()


    @staticmethod
    def hasfinishTextorEnmienda(key):
        return [ i for i in AmendmentFlow.getKeys() if key == i]



    @staticmethod
    def checkTypeAmendment(type,array, serie):
        tpe = AmendmentFlow.hasfinishTextorEnmienda(type)
        if tpe:
            amendtexts = AmendmentFlow.getTextAmendment(type)
            amendserie = AmendmentFlow.getTypeBol(type)
            if amendserie == serie:
                for element in array:
                    for texa in amendtexts:
                        if re.search(texa,element,re.IGNORECASE):
                            return True
            return None
        else:
            return None

    @staticmethod
    def checkTextodefinitivoarray(type,array,aprobdef):
        tpe = AmendmentFlow.hasfinishTextorEnmienda(type)
        if tpe:
            if aprobdef:
                for element in array:
                    if re.search("aprobaci(.+?)n(.*?)definitiva", element, re.IGNORECASE):
                        return True
                return None

            else:
                amendfinish = AmendmentFlow.getFinishText(type)
                for element in array:
                    for texa in amendfinish:
                        if re.search(texa, element, re.IGNORECASE):
                            return True
                return None
        else:
            return None

    @staticmethod
    def hasAprobDef(boletines):
        hastextosenado = False
        hasaprobdef = False
        for bol in boletines:
            for element in bol.xpath("text()").extract():
                if re.search("texto(.*?)aprobado(.*?)senado",element,re.IGNORECASE):
                    hastextosenado = True
                if hastextosenado:
                    if re.search("aprobaci(.+?)n(.*?)definitiva",element, re.IGNORECASE):
                        hasaprobdef = True

        return hasaprobdef











