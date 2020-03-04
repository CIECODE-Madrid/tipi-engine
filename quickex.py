import sys

from alerts.send_alerts import SendAlerts
from data_cleaners.transformations import run_cleaner
from labeling.motor_pcre import LabelingEngine
from stats.process_stats import GenerateStats


def print_help():
    print('Usage: quickex.py TASK')
    print('Apply task: alerts, labeling, stats or cleaner')
    print('Example: python quickex.py stats')


args = sys.argv
if len(args) == 2:
    if args[1] == 'alerts':
        SendAlerts()
    elif args[1] == 'labeling':
        labeling_engine = LabelingEngine()
        labeling_engine.run()
    elif args[1] == 'stats':
        GenerateStats()
    elif args[1] == 'cleaner':
        run_cleaner()
    else:
        print('quickex: invalid TASK')
        print_help()
else:
    print('quickex: bad number of params')
    print_help()
