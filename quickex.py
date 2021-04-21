import sys

from extractors.extractor import ExtractorTask
from tagger.tag_initiatives import TagInitiatives
from alerts.send_alerts import SendAlerts
from stats.process_stats import GenerateStats


def print_help():
    print('Usage: quickex.py TASK')
    print('Apply task: alerts, tagger, stats or extractor')
    print('Example: python quickex.py stats')

def send_alerts(args):
    SendAlerts()

def tag(args):
    TagInitiatives().run()

def stats(args):
    GenerateStats().generate()

def extract(args):
    task = ExtractorTask()
    subcommands = {
        'references': task.references,
        'initiatives': task.initiatives,
        'members': task.members
    }

    if len(args) > 2 and args[2] in subcommands:
        return subcommands[args[2]]()
    task.run()

commands = {
    'alerts': send_alerts,
    'tagger': tag,
    'stats': stats,
    'extractor': extract
}

args = sys.argv
if len(args) > 1:
    if args[1] in commands:
        commands[args[1]](args)
    else:
        print('quickex: invalid TASK')
        print_help()
else:
    print('quickex: bad number of params')
    print_help()
