from .initiative_extractors.bulletins_extractor import \
        ABulletinsExtractor, \
        BBulletinsExtractor, \
        CBulletinsExtractor, \
        DBulletinsExtractor, \
        EBulletinsExtractor, \
        FirstABulletinExtractor, \
        FirstBBulletinExtractor, \
        FirstCBulletinExtractor, \
        FirstDBulletinExtractor, \
        FirstEBulletinExtractor, \
        NonExclusiveBulletinExtractor, \
        BulletinAndSenateExtractor

from .initiative_extractors.question_extractor import QuestionExtractor
from .initiative_extractors.boe_extractor import BoeExtractor, FirstBoeExtractor


INITIATIVE_TYPES = [
        {
                "type": "Proyecto de ley",
                "code": "121",
                "group": "Función legislativa",
                "class": FirstABulletinExtractor
                }
]
