import luigi

from alerts.alerts import GenerateAlertsTask
from utils import clean_files, FILES
from .process_stats import GenerateStats


class GenerateStatsTask(luigi.Task):
    task_namespace = 'stats'

    def requires(self):
        return GenerateAlertsTask()


    def run(self):
        print("{task} says: ready to generate stats!".format(task=self.__class__.__name__))
        GenerateStats()
        clean_files()
