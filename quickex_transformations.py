from importlib import import_module as im

from data_cleaners.config import MODULE_DATA_CLEANER as CLEANER

populate_status = im('data_cleaners.{}.populate_status'.format(CLEANER))
convert_urls = im('data_cleaners.{}.convert_urls'.format(CLEANER))


if __name__ == '__main__':
    populate_status.PopulateStatus().populate()
    convert_urls.ConvertURLs().convert()
