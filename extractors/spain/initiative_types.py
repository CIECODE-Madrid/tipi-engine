from .initiative_extractors.one_bulletin_extractor import \
        OneABulletinExtractor, \
        OneBBulletinExtractor, \
        OneDBulletinExtractor, \
        OneEBulletinExtractor

from .initiative_extractors.question_extractor import QuestionExtractor
from .initiative_extractors.boe_extractor import BoeExtractor, FirstBoeExtractor


INITIATIVE_TYPES = [
        {
            "type": "Competencias en relación con la Corona",
            "code": "070",
            "group": "Competencias en relación con la Corona"
            },
        {
            "type": "Propuesta de candidato a la Presidencia del Gobierno",
            "code": "080",
            "group": "Confianza parlamentaria",
            "class": OneDBulletinExtractor
            },
        {
            "type": "Moción de censura",
            "code": "082",
            "group": "Confianza parlamentaria"
            },
        {
            "type": "Moción de reprobación a miembros del Gobierno",
            "code": "084",
            "group": "Confianza parlamentaria"
            },
        {
            "type": "Proyecto de reforma Constitucional",
            "code": "102",
            "group": "Reforma constitucional",
            "class": OneABulletinExtractor
            },
        {
            "type": "Proposición de reforma Constitucional de Grupos Parlamentarios",
            "code": "100",
            "group": "Reforma constitucional",
            "class": OneBBulletinExtractor
            },
        {
            "type": "Proposición de reforma constitucional de Comunidades Autónomas",
            "code": "101",
            "group": "Reforma constitucional",
            "class": OneBBulletinExtractor
            },
        {
            "type": "Autorización de Convenios Internacionales",
            "code": "110",
            "group": "Convenios Internacionales",
            "class": OneABulletinExtractor
            },
        {
            "type": "Información sobre Convenios Internacionales (art. 94.2 Const.)",
            "code": "111",
            "group": "Convenios Internacionales",
            "class": FirstBoeExtractor
            },
        {
            "type": "Otros asuntos relativos a Convenios Internacionales",
            "code": "112",
            "group": "Convenios Internacionales"
            },
        {
                "type": "Proyecto de ley",
                "code": "121",
                "group": "Función legislativa",
                "class": OneABulletinExtractor
                },
        {
                "type": "Proposición de ley de Grupos Parlamentarios del Congreso",
                "code": "122",
                "group": "Función legislativa",
                "class": OneBBulletinExtractor
                },
        {
                "type": "Proposición de ley de Diputados",
                "code": "123",
                "group": "Función legislativa",
                "class": OneBBulletinExtractor
                },
        {
                "type": "Proposición de ley del Senado",
                "code": "124",
                "group": "Función legislativa",
                "class": OneBBulletinExtractor
                },
        {
                "type": "Proposición de ley de Comunidades y Ciudades Autónomas",
                "code": "125",
                "group": "Función legislativa",
                "class": OneBBulletinExtractor
                },
        {
                "type": "Propuesta de reforma de Estatuto de Autonomía",
                "code": "127",
                "group": "Función legislativa",
                "class": OneBBulletinExtractor
                },
        {
                "type": "Iniciativa legislativa popular",
                "code": "120",
                "group": "Función legislativa",
                "class": OneBBulletinExtractor # TODO Retrieves all Bs?
                },
        {
                "type": "Real Decreto-Ley",
                "code": "130",
                "group": "Función legislativa"
                },
        {
                "type": "Real Decreto legislativo que aprueba texto refundido",
                "code": "132",
                "group": "Función legislativa",
                "class": FirstBoeExtractor
                },
        {
                "type": "Real Decreto legislativo que aprueba texto refundido",
                "code": 132,
                "group": "Función legislativa",
                "class": FirstBoeExtractor
                },
        {
                "type": "Real Decreto legislativo en desarrollo de Ley de Bases",
                "code": "131",
                "group": "Función legislativa",
                "class": OneEBulletinExtractor
                },
        {
                "type": "Interpelación urgente",
                "code": "172",
                "group": "Función de control"
                },
        {
                "type": "Interpelación ordinaria",
                "code": "170",
                "group": "Función de control"
                },
        {
                "type": "Pregunta oral en Pleno",
                "code": "180",
                "group": "Función de control"
                },
        {
                "type": "Pregunta oral al Gobierno en Comisión",
                "code": "181",
                "group": "Función de control"
                },
        {
                "type": "Pregunta al Gobierno con respuesta escrita",
                "code": "184",
                "group": "Función de control",
                "class": QuestionExtractor
                },
        {
                "type": "Pregunta oral a la Corporación RTVE",
                "code": "178",
                "group": "Función de control"
                },
        {
                "type": "Pregunta a la Corporación RTVE con respuesta escrita",
                "code": "179",
                "group": "Función de control"
                },
        {
                "type": "Comparecencia del Gobierno ante el Pleno",
                "code": "210",
                "group": "Función de control"
                },
        {
                "type": "Comparecencia del Gobierno en Comisión (art. 44)",
                "code": "213",
                "group": "Función de control"
                },
        {
                "type": "Comparecencia del Gobierno en Comisión (arts. 202 y 203)",
                "code": "214",
                "group": "Función de control"
                },
        {
                "type": "Comparecencia del Gobierno en Comisión Mixta solicitada en el Senado",
                "code": "221",
                "group": "Función de control"
                },
        {
                "type": "Comparecencia de autoridades y funcionarios en Comisión",
                "code": "212",
                "group": "Función de control"
                },
        {
                "type": "Comparec. autoridades y funcionarios en Com. Mx. solicitada en Senado",
                "code": "222",
                "group": "Función de control"
                },
        {
                "type": "Otras comparecencias en Comisión",
                "code": "219",
                "group": "Función de control"
                },
        {
                "type": "Otras comparecencias en Comisión Mixta solicitadas en el Senado",
                "code": "223",
                "group": "Función de control"
                },
        {
                "type": "Funciones de la Diputación Permanente",
                "code": "062",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a la Administración del Estado (art. 7)",
                "code": "186",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a Comunidad Autónoma (art. 7)",
                "code": "187",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a Entidad Local (art. 7)",
                "code": "188",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a otra Entidad Pública (art. 7)",
                "code": "189",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a la Administración del Estado (art. 44)",
                "code": "193",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a Comunidad Autónoma (art. 44)",
                "code": "194",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a Entidad Local (art. 44)",
                "code": "195",
                "group": "Función de control"
                },
        {
                "type": "Solicitud de informe a otra Entidad Pública (art. 44)",
                "code": "196",
                "group": "Función de control"
                },
        {
                "type": "Otras solicitudes de informe (art. 44)",
                "code": "197",
                "group": "Función de control"
                },
        {
                "type": "Información sobre secretos oficiales",
                "code": "224",
                "group": "Función de control"
                },
        {
                "type": "Documentación remitida a Comisiones para su conocimiento",
                "code": "043",
                "group": "Función de control"
                },
        {
                "type": "Documentación remitida a Comisiones para su eventual tramitación",
                "code": "044",
                "group": "Función de control"
                },
        {
                "type": "Operaciones de las Fuerzas Armadas en el exterior",
                "code": "095",
                "group": "Función de control"
                },
        {
                "type": "Proposición no de Ley ante el Pleno",
                "code": "162",
                "group": "Función de orientación política"
                },
        {
                "type": "Proposición no de Ley en Comisión",
                "code": "161",
                "group": "Función de orientación política"
                },
        {
                "type": "Moción consecuencia de interpelación ordinaria",
                "code": "171",
                "group": "Función de orientación política"
                },
        {
                "type": "Moción consecuencia de interpelación urgente",
                "code": "173",
                "group": "Función de orientación política"
                },
        {
                "type": "Planes y programas",
                "code": "201",
                "group": "Función de orientación política"
                },
        {
                "type": "Comunicación del Gobierno",
                "code": "200",
                "group": "Función de orientación política"
                },
        {
                "type": "Propuesta de resolución relativa al art 11 de la Ley Orgánica 6/2002 de Partidos Políticos",
                "code": "",
                "group": "Función de orientación política"
                },
        {
                "type": "Objetivo de estabilidad presupuestaria",
                "code": "430",
                "group": "Función de orientación política"
                },
        {
                "type": "Funciones de las Comisiones",
                "code": "042",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Comisión permanente (art. 50)",
                "code": "151",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Solicitud de creación de Comisión permanente (art. 50)",
                "code": "155",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Comisión de Investigación (art. 52)",
                "code": "152",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Solicitud de creación de Comisión de Investigación (art. 52)",
                "code": "156",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Grupo de trabajo",
                "code": "159",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Subcomisiones y Ponencias",
                "code": "154",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Solicitud de creación de Subcomisiones y Ponencias",
                "code": "158",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Otras Comisiones no permanentes (art. 53)",
                "code": "153",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Solicitud de creación de otras Comisiones no permanentes (art. 53)",
                "code": "157",
                "group": "Comisiones, subcomisiones y ponencias"
                },
        {
                "type": "Actos en relación con los estados de alarma, excepción y sitio",
                "code": "091",
                "group": "Actos en relación con los estados de alarma, excepción y sitio"
                },
        {
                "type": "Convenios entre Comunidades Autónomas",
                "code": "093",
                "group": "Actos en relación con las Comunidades Autónomas"
                },
        {
                "type": "Otros actos en relación con las Comunidades Autónomas",
                "code": "094",
                "group": "Actos en relación con las Comunidades Autónomas"
                },
        {
                "type": "Proposición de reforma del Reglamento del Congreso",
                "code": "410",
                "group": "Reglamento del Congreso",
                "class": OneBBulletinExtractor
                },
        {
                "type": "Resolución de la Presidencia del Congreso",
                "code": "411",
                "group": "Reglamento del Congreso"
                },
        {
                "type": "Otros asuntos relativos al Reglamento del Congreso",
                "code": "412",
                "group": "Reglamento del Congreso"
                },
        {
                "type": "Resoluciones normativas de las Cortes Generales",
                "code": "413",
                "group": "Reglamento del Congreso",
                "class": OneABulletinExtractor
                },
        {
                "type": "Resoluciones normativas del Congreso",
                "code": "414",
                "group": "Reglamento del Congreso",
                "class": OneABulletinExtractor
                },
        {
                "type": "Funciones de la Mesa de la Cámara",
                "code": "023",
                "group": "Reglamento del Congreso"
                },
        {
                "type": "Conflicto de competencia ante el Tribunal Constitucional",
                "code": "",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Recurso previo contra Convenios Internacionales",
                "code": "",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Recurso de inconstitucionalidad",
                "code": "232",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Cuestión de inconstitucionalidad",
                "code": "233",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Recurso de amparo",
                "code": "234",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Nombramientos para el Tribunal Constitucional",
                "code": "235",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Suplicatorio",
                "code": "240",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Nombramientos de miembros del Consejo General del Poder Judicial",
                "code": "244",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Memoria del Consejo General del Poder Judicial",
                "code": "245",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Memoria de la Fiscalía General del Estado",
                "code": "285",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Cuenta General del Estado",
                "code": "250",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Informe del Tribunal de Cuentas",
                "code": "251",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Solicitud de fiscalización del Tribunal de Cuentas",
                "code": "253",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Otros asuntos relativos al Tribunal de Cuentas",
                "code": "259",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Informe anual del Defensor del Pueblo",
                "code": "260",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Otros informes del Defensor del Pueblo",
                "code": "261",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Nombramientos del Defensor del Pueblo y Adjuntos",
                "code": "262",
                "group": "Relaciones con órganos e instituciones públicas",
                "class": BoeExtractor
                },
        {
                "type": "Informe anual del Consejo de Seguridad Nuclear",
                "code": "401",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Memoria anual de la Corporación RTVE",
                "code": "440",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Informe anual de la Corporación RTVE",
                "code": "442",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Elección de miembros de otros órganos",
                "code": "276",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Control de la aplicación del principio de subsidiariedad",
                "code": "282",
                "group": "Relaciones con órganos e instituciones públicas"
                },
        {
                "type": "Declaración Institucional",
                "code": "140",
                "group": "Declaración Institucional"
                },
        {
                "type": "Declaración de actividades",
                "code": "004",
                "group": "Declaración de actividades"
                },
        {
                "type": "Declaración de bienes y rentas",
                "code": "005",
                "group": "Declaración de bienes y rentas"
                },
        {
                "type": "Normas relativas a la org. y func. de la Secretaría General",
                "code": "291",
                "group": "Secretaría general"
                },
        {
                "type": "Normas sobre personal y org. administrativa de las Cortes Generales",
                "code": "294",
                "group": "Secretaría general"
                },
        {
                "type": "Actos sobre personal y org. administrativa de las Cortes Generales",
                "code": "295",
                "group": "Secretaría general"
                },
        {
                "type": "Personal eventual del Congreso de los Diputados",
                "code": "299",
                "group": "Secretaría general"
                }
]
