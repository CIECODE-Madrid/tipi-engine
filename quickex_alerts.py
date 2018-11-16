from alerts.search import NotifyByEmail
import sys

reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':
    NotifyByEmail()
