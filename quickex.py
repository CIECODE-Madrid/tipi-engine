import sys

from extractors.extractor import ExtractorTask
from tagger.tag_initiatives import TagInitiatives
from alerts.send_alerts import SendAlerts
from stats.process_stats import GenerateStats


def print_help():
    print('Usage: quickex.py TASK')
    print('Apply task: alerts, tagger, stats or extractor')
    print('Example: python quickex.py stats')


args = sys.argv
if len(args) == 2:
    if args[1] == 'alerts':
        SendAlerts()
    elif args[1] == 'tagger':
        TagInitiatives().run()
    elif args[1] == 'stats':
        GenerateStats()
    elif args[1] == 'extractor':
        ExtractorTask().run()
    else:
        print('quickex: invalid TASK')
        print_help()
else:
    print('quickex: bad number of params')
    print_help()
