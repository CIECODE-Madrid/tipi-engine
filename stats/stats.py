import luigi
from alerts.alerts import GenerateAlertsTask
from stats.process_stats import InsertStats
from utils import clean_files, FILES
import pdb

class GenerateStatsTask(luigi.Task):
    task_namespace = 'stats'

    def requires(self):
        return GenerateAlertsTask()


    def run(self):
        print("{task} says: ready to generate stats!".format(task=self.__class__.__name__))
        InsertStats()
        clean_files()
