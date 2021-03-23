import luigi

from .send_alerts import SendAlerts
from .settings import USE_ALERTS
from tagger.tagger import TaggerTask
from targets import *
from utils import FILES


class GenerateAlertsTask(luigi.Task):
    task_namespace = 'alerts'

    def requires(self):
        return TaggerTask()

    def output(self):
        return luigi.LocalTarget(FILES[2])

    def run(self):
        print("{task} says: ready to generate alerts!".format(task=self.__class__.__name__))
        if USE_ALERTS:
            SendAlerts()
        self.output().open('w').close()
