from transformations.populate_status import PopulateStatus
from transformations.convert_urls import ConvertURLs


if __name__ == '__main__':
    PopulateStatus().populate()
    ConvertURLs().convert()
