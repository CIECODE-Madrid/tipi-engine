from transformations.populate_status import PopulateStatus
from transformations.convert_urls import ConvertURLs
from transformations.clean_contents import CleanContents


if __name__ == '__main__':
    PopulateStatus().populate()
    ConvertURLs().convert()
    CleanContents().clean()
