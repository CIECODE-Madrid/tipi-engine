from transformations.populate_status import PopulateStatus
from transformations.convert_urls import ConvertURLs
import sys

reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':
    PopulateStatus().populate()
    ConvertURLs().convert()
