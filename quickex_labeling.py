from labeling.motor_pcre import LabelingEngine
import sys

reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':
    labeling_engine = LabelingEngine()
    labeling_engine.run()
