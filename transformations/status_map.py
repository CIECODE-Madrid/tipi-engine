# -*- coding: utf-8 -*-

STATUS_MAP = {
        'Aprobada': {
            'processing': [
                "Aprobado con modificaciones",
                "Aprobado sin modificaciones",
                "Convalidado",
                "Tramitado por completo sin"
                ],
            "initiative_type_alt": [
                "Información sobre Convenios Internacionales",
                "Otros asuntos relativos a Convenios Internacionales",
                "Real Decreto Legislativo",
                "Declaración Institucional",
                "Solicitud de Comparecencia ante el Pleno",
                "Solicitud de comparecencia en Comisión",
                "Solicitud de comparecencia de autoridades y funcionarios en Comisión",
                "Solicitud de comparecencia del Gobierno en Comisión",
                "Solicitud de Comparecencia en Comisión"
                ]
            },
        "Rechazada": {
            "processing": [
                "Rechazado"
                ]
            },
        "Respondida": {
            "processing": [
                "Tramitado por completo sin",
                "Gobierno Reclamación"
                ],
            "initiative_type_alt": [
                "Interpelación urgente",
                "Pregunta oral en Pleno",
                "Pregunta oral al Gobierno en Comisión",
                "Pregunta al Gobierno con respuesta escrita",
                "Respuesta"
                ]
            },
        "Celebrada": {
            "processing": [
                "Tramitado por completo sin"
                ],
            "initiative_type_alt": [
                "Comparecencia en Comisión",
                "Comparecencia de autoridades y funcionarios en Comisión",
                "Comparecencia del Gobierno en Comisión",
                "Otras comparecencias en Comisión"
                ]
            },
        "En tramitación": {
            "processing": [
                "Boletín Oficial de las Cortes Generales Publicación desde",
                "Comisión.*desde",
                "Concluido desde",
                "Gobierno Contestación",
                "Junta de Portavoces",
                "Mesa del Congreso Acuerdo",
                "Mesa del Congreso Requerimiento",
                "Mesa del Congreso Calificación",
                "Mesa del Congreso Reclamación",
                "Pleno Aprobación desde",
                "Pleno desde",
                "Pleno Toma en consideración",
                "Solicitud de amparo",
                "Respuesta.*Gobierno",
                "Senado desde",
                ],
            },
        "No admitida a trámite": {
                "processing": [
                    "Inadmitido a trámite"
                    ]
                },
        "No debatida": {
                "processing": [
                    "Decaído"
                    ]
                },
        "Retirada": {
                "processing": [
                    "Retirado",
                    "Extinguido por desaparición o cese del autor"
                    ]
                },
        "Convertida en otra": {
                "processing": [
                    "Convertido"
                    ]
                },
        "Acumulada en otra": {
                "processing": [
                    "Subsumido en otra iniciativa"
                    ]
                }
        }
