# -*- coding: utf-8 -*-

STATUS_MAP = [
        {
            'search': {'processing': {'$regex': 'Aprobado con modificaciones', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'processing': {'$regex': 'Aprobado sin modificaciones', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'processing': {'$regex': 'Convalidado', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'processing': {'$regex': 'Tramitado con propuestas de resolución', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'processing': {'$regex': 'Entidad Pública Contestación', '$options': 'gi'}},
            'status': 'Respondida'
        },
        {
            'search': {'processing': {'$regex': 'Pleno Contestación', '$options': 'gi'}},
            'status': 'Respondida'
        },
        {
            'search': {'processing': {'$regex': 'Tramitado por completo sin', '$options': 'gi'}, 'initiative_type': {'$in': ["171", "180", "181", "184"]}},
            'status': 'Respondida'
        },
        {
            'search': {'processing': {'$regex': 'Tramitado por completo sin', '$options': 'gi'}, 'initiative_type': {'$in': ["212", "213", "214", "219"]}},
            'status': 'Celebrada'
        },
        {
            'search': {'processing': {'$regex': 'Tramitado por completo sin', '$options': 'gi'}, 'initiative_type': {'$not': {'$in': ["171", "180", "181", "184", "212", "213", "214", "219"]}}},
            'status': 'Aprobada'
        },
        {
            'search': {'processing': {'$regex': 'Convertido', '$options': 'gi'}},
            'status': 'Convertida en otra'
        },
        {
            'search': {'$or': [
                {'processing': {'$regex': "Boletín Oficial de las Cortes Generales Publicación desde", '$options': 'gi'}},
                {'processing': {'$regex': "Comisión.*desde", '$options': 'gi'}},
                {'processing': {'$regex': "Concluido desde", '$options': 'gi'}},
                {'processing': {'$regex': "Gobierno Contestación", '$options': 'gi'}},
                {'processing': {'$regex': "Gobierno Reclamación", '$options': 'gi'}},
                {'processing': {'$regex': "Junta de Portavoces", '$options': 'gi'}},
                {'processing': {'$regex': "Mesa del Congreso Acuerdo", '$options': 'gi'}},
                {'processing': {'$regex': "Mesa del Congreso Requerimiento", '$options': 'gi'}},
                {'processing': {'$regex': "Mesa del Congreso Calificación", '$options': 'gi'}},
                {'processing': {'$regex': "Mesa del Congreso Reclamación", '$options': 'gi'}},
                {'processing': {'$regex': "Pleno Aprobación desde", '$options': 'gi'}},
                {'processing': {'$regex': "Pleno desde", '$options': 'gi'}},
                {'processing': {'$regex': "Pleno Toma en consideración", '$options': 'gi'}},
                {'processing': {'$regex': "Solicitud de amparo", '$options': 'gi'}},
                {'processing': {'$regex': "Respuesta.*Gobierno", '$options': 'gi'}},
                {'processing': {'$regex': "Senado desde", '$options': 'gi'}},
                {'processing': {'$regex': "Junta Electoral Central desde", '$options': 'gi'}}
                ]},
            'status': 'En tramitación'
        },
        {
            'search': {'processing': {'$regex': 'Subsumido en otra iniciativa', '$options': 'gi'}},
            'status': 'Acumulada en otra'
        },
        {
            'search': {'processing': {'$regex': 'Inadmitido a trámite', '$options': 'gi'}},
            'status': 'No admitida a trámite'
        },
        {
            'search': {'processing': {'$regex': 'Decaído', '$options': 'gi'}},
            'status': 'No debatida'
        },
        {
            'search': {'processing': {'$regex': 'Rechazado', '$options': 'gi'}},
            'status': 'Rechazada'
        },
        {
            'search': {'processing': {'$regex': 'Retirado', '$options': 'gi'}},
            'status': 'Retirada'
        },
        {
            'search': {'processing': {'$regex': 'No celebración', '$options': 'gi'}},
            'status': 'No celebrada'
        },
        {
            'search': {'processing': {'$regex': 'Derogado', '$options': 'gi'}},
            'status': 'Derogada'
        },
        {
            'search': {'processing': {'$regex': 'Extinguido', '$options': 'gi'}},
            'status': 'Extinguida'
        },
        {
            'search': {'processing': {'$regex': 'Caducado', '$options': 'gi'}},
            'status': 'Caducada'
        },
        {
            'search': {'processing': {'$regex': 'Desconocida', '$options': 'gi'}},
            'status': 'Desconocida'
        }
    ]
