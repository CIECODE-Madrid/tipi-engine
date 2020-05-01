from .legislative_period import LegislativePeriod


class InitiativesExtractor:
    def __init__(self):
        self.__legislative_period = LegislativePeriod().get()

    def extract(self):
        pass
