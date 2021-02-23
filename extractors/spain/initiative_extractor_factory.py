from .initiative_extractors.initiative_extractor import InitiativeExtractor

class InitiativeExtractorFactory:
    @staticmethod
    def create(response, deputies, parliamentarygroups, places):
        initiative_types_mapping = {}
        response_type = ''
        if response_type in initiative_types_mapping:
            extractor = initiative_types_mapping.get(response_type)(response, deputies, parliamentarygroups, places)
            return extractor

        return InitiativeExtractor(response, deputies, parliamentarygroups, places)

