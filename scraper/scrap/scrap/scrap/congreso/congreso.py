# -*- coding: utf-8 -*-
import re

from conn import MongoDBconn
import pdb

class Congress(object):
    _conn = None
    def __init__(self):
        self._conn = MongoDBconn()

    def _getCollection(self,collection):
        return self._conn.getDB()[collection]

    def searchAll(self,collection=None):
        return [ element for element in self._getCollection(collection).find()]



    def getInitiative(self, collection="iniciativas", ref = None, tipotexto= None, titulo = None):
        search = self._getCollection(collection).find_one(
            {
                'ref': ref,
                'tipotexto': tipotexto,
                'titulo': titulo
            }
        )
        return search


    def updateorinsertInitiative(self, collection="iniciativas", type = "insert", item = None):
        #metodo para el pipeline
        if type is 'insert':
            self._insertInitiative(collection,item)
            #update
        elif type is 'update':
            self._updateInitiative(collection,item)
            #inserta
        else:
            print "Not type accepted"
            raise

    def _insertInitiative(self,collection,item):
        self._getCollection(collection=collection).insert(dict(item))

    def _updateInitiative(self,collection,item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
                 'ref': item['ref'],
                'tipotexto': item['tipotexto'],


        },{
            '$set': {
            'titulo': item['titulo'],
            'autor_diputado': item['autor_diputado'],
            'autor_grupo': item['autor_grupo'],
            'autor_otro': item['autor_otro'],
            'url': item['url'],
            'tipo': item['tipo'],
            'tramitacion': item['tramitacion'],
            'fecha': item['fecha'],
            'lugar': item['lugar'],
            'fechafin': item['fechafin'],

                    }
            ,}
        )



    def updateorinsertInitiativecontent(self, collection="iniciativas", type = "insert", item = None):
        #metodo para el pipeline
        if type is 'insert':
            self._insertInitiative(collection,item)
            #update
        elif type is 'update':
            self._updateInitiativecontent(collection,item)
            #inserta
        else:
            print "Not type accepted"
            raise



    def _updateInitiativecontent(self,collection,item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
                 'ref': item['ref'],
                'tipotexto': item['tipotexto'],


        },{
            '$set': {
            'titulo': item['titulo'],
            'autor_diputado': item['autor_diputado'],
            'autor_grupo': item['autor_grupo'],
            'autor_otro': item['autor_otro'],
            'url': item['url'],
            'tipo': item['tipo'],
            'tramitacion': item['tramitacion'],
            'fecha': item['fecha'],
            'lugar': item['lugar'],
            'fechafin': item['fechafin'],
            'contenido': item['contenido'],

                    }
            ,}
        )




    def isDiffinitiative(self, collection="iniciativas", item = None, search = None):


        if search:#existe
            return not self.sameInitiative(item,search)
        else:
            return False

    def sameInitiative(self,item,search):
        if len(item.keys()) != len(search.keys())-1: # se descarta el content
            return False
        else:
            for key, value in search.iteritems():
                for ikey,ivalue in item.iteritems():
                    if key == ikey:
                        if value !=  ivalue and  key is not 'contenido':

                            return False
            return True


    def updateorinsertAdmenment(self, collection="iniciativas",  item = None ,search = None):
        #metodo para el pipeline

        self._insertAdmendment(collection,item,search)
            #update


    def _insertAdmendment(self,collection,item,search):

        if not search:
            insert ={
                'ref': item['ref'],
                'tipotexto':item['tipotexto'],
                'titulo': item['titulo'],
                'tipo':item['tipo'],
                'autor_grupo': item["autor_grupo"],
                'autor_diputado':item["autor_diputado"],
                'autor_otro' : item["autor_otro"],
                'fecha': item["fecha"],
                'fechafin': item["fechafin"],
                'url': item['url'],
                'lugar': item['lugar'],
                'tramitacion': item['tramitacion'],
                'contenido':[item["contenido"]]


            }
            self._getCollection(collection=collection).insert(insert)
        else:
            self._updateAdmendment(collection,item,search)

    def _updateAdmendment(self,collection,item,search):

        autor = item["autor_grupo"]

        coll = self._getCollection(collection=collection)
        append = item["contenido"]
        before = search["contenido"]
        beforeautor = search["autor_diputado"]
        beforeotro = search["autor_otro"]
        if item["autor_diputado"]:
            beforeautor = beforeautor + item["autor_diputado"]
        if item["autor_otro"]:
            beforeotro=beforeotro+item["autor_otro"]
        if append not in before:
            before.append(append)
            coll.update_one({
                        'ref': item['ref'],
                        'tipotexto': item['tipotexto'],
                        'autor_grupo' : autor


                },{
                    '$set': {
                    'autor_diputado': list(set(beforeautor)),
                    'autor_otro': list(set(beforeotro)),
                    'contenido':before,
                            }
                    ,}
                )

    def getAdmendment(self, collection="iniciativas", ref = None, tipotexto= None, autor = None):
        search = self._getCollection(collection).find_one(
        {
                'ref': ref,
                'tipotexto': tipotexto,
                'autor_grupo': autor
        }
        )

        return search


    def updateorinsertFinishtextorResponse(self, collection="iniciativas", type="insert", item=None):
            # metodo para el pipeline
        if type is 'insert':
            self._insertFinishsTextorResponse(collection, item)
                # update
        elif type is 'update':
            self._updateFinishTextorResponse(collection, item)
                # inserta
        else:
            print "Not type accepted"
            raise

    def _insertFinishsTextorResponse(self, collection, item):
        self._getCollection(collection=collection).insert(dict(item))

    def _updateFinishTextorResponse(self, collection, item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
                'ref': item['ref'],
                'tipotexto': item['tipotexto'],

            }, {
                '$set': {
                    'titulo': item['titulo'],
                    'autor_diputado': item['autor_diputado'],
                    'autor_grupo': item['autor_grupo'],
                    'autor_otro': item['autor_otro'],
                    'url': item['url'],
                    'tipo': item['tipo'],
                    'tramitacion': item['tramitacion'],
                    'fecha': item['fecha'],
                    'lugar': item['lugar'],
                    'fechafin': item['fechafin'],
                    'contenido': item['contenido']

                }
                ,}
            )

    def getMember(self, collection="diputados", name = None):
        search = self._getCollection(collection).find_one(
            {
                'nombre': name,
            }
        )
        return search


    def updateorinsertMember(self, collection="diputados", type = "insert", item = None):
        #metodo para el pipeline
        if type is 'insert':
            self._insertMember(collection,item)
            #update
        elif type is 'update':
            self._updateMember(collection,item)
            #inserta
        else:
            print "Not type accepted"
            raise

    def _insertMember(self, collection, item):
        self._getCollection(collection=collection).insert(dict(item))

    def _updateMember(self, collection, item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
            'nombre': item['nombre'],


        }, {
            '$set': {
                'url': item['url'],
                'grupo': item['grupo'],
                'correo': item['correo'],
                'web': item['web'],
                'url': item['url'],
                'twitter': item['twitter'],
                'fecha_alta': item['fecha_alta'],
                'fecha_baja': item['fecha_baja'],
                'imagen': item['imagen']

            }
        })








