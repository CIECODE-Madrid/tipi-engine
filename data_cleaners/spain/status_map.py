UNKNOWN = 'Desconocida'

STATUS_MAP = [
        {
            'search': {'$or': [
                {'extra.latest_history_item': {'$regex': "Boletín Oficial de las Cortes Generales Publicación desde", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Comisión.*desde", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Gobierno Contestación", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Gobierno Reclamación", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Junta de Portavoces", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Mesa del Congreso Acuerdo", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Mesa del Congreso Requerimiento", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Mesa del Congreso Calificación", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Mesa del Congreso Reclamación", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Pleno Aprobación desde", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Pleno desde", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Pleno Toma en consideración", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Solicitud de amparo", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Respuesta.*Gobierno", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Senado desde", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': "Junta Electoral Central desde", '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': 'Administración del Estado Contestación', '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': 'Entidad Pública Contestación', '$options': 'gi'}},
                {'extra.latest_history_item': {'$regex': 'Pleno Contestación', '$options': 'gi'}},
                ]},
            'status': 'En tramitación'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Aprobado con modificaciones', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Aprobado sin modificaciones', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Convalidado', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Tramitado con propuestas de resolución', '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': "Concluido desde", '$options': 'gi'}},
            'status': 'Aprobada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Tramitado por completo sin', '$options': 'gi'}, 'initiative_type': {'$not': {'$in': ["170", "172", "180", "181", "184", "212", "213", "214", "219"]}}},
            'status': 'Aprobada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Tramitado por completo sin', '$options': 'gi'}, 'initiative_type': {'$in': ["170", "172", "180", "181", "184"]}},
            'status': 'Respondida'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Tramitado por completo sin', '$options': 'gi'}, 'initiative_type': {'$in': ["212", "213", "214", "219"]}},
            'status': 'Celebrada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Convertido', '$options': 'gi'}},
            'status': 'Convertida en otra'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Subsumido en otra iniciativa', '$options': 'gi'}},
            'status': 'Acumulada en otra'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Inadmitido a trámite', '$options': 'gi'}},
            'status': 'No admitida a trámite'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Decaído', '$options': 'gi'}},
            'status': 'No debatida'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Rechazado', '$options': 'gi'}},
            'status': 'Rechazada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Retirado', '$options': 'gi'}},
            'status': 'Retirada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'No celebración', '$options': 'gi'}},
            'status': 'No celebrada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Derogado', '$options': 'gi'}},
            'status': 'Derogada'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Extinguido', '$options': 'gi'}},
            'status': 'Extinguida'
        },
        {
            'search': {'extra.latest_history_item': {'$regex': 'Caducado', '$options': 'gi'}},
            'status': 'Caducada'
        },
        {
            'search': {'extra.latest_history_item': UNKNOWN},
            'status': UNKNOWN
        },
        {
            'search': {'extra.latest_history_item': ''},
            'status': UNKNOWN
        }
    ]
