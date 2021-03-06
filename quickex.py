import sys

from extractors.extractor import ExtractorTask
from tagger.tag_initiatives import TagInitiatives
from untagger.untag_initiatives import UntagInitiatives
from alerts.send_alerts import SendAlerts
from stats.process_stats import GenerateStats


def print_help():
    print('Usage: quickex.py TASK')
    print('Apply task: alerts, tagger, untagger, stats or extractor')
    print('Example: python quickex.py stats')

def run_command(commands, arguments):
    if len(args) > 2:
        if args[2] in commands:
            args_amount = len(args)
            if args_amount == 4:
                return commands[args[2]](args[3])
            if args_amount == 5:
                return commands[args[2]](args[3], args[4])
            else:
                return commands[args[2]]()
        else:
            print('quickex: invalid TASK')
            return
    commands['default']()

def send_alerts(args):
    SendAlerts()

def modify_regex(tag):
    tagger = TagInitiatives()
    untagger = UntagInitiatives()

    untagger.remove_tag(tag)
    tagger.new_tag(tag)


def tag(args):
    command = TagInitiatives()
    subcommands = {
        'all': command.run,
        'new-tag': command.new_tag,
        'new-topic': command.new_topic,
        'modify-regex': modify_regex,
        'rename-tag': command.rename,
        'default': command.run
    }
    run_command(subcommands, args)

def stats(args):
    GenerateStats().generate()

def untag(args):
    command = UntagInitiatives()
    subcommands = {
        'all': command.untag_all,
        'undo': command.undo,
        'topic': command.by_topic,
        'tag': command.by_tag,
        'remove-topic': command.remove_topic,
        'remove-tag': command.remove_tag,
        'default': command.untag_all
    }
    run_command(subcommands, args)

def extract(args):
    task = ExtractorTask()
    subcommands = {
        'initiatives': task.initiatives,
        'references': task.references,
        'votes': task.votes,
        'interventions': task.interventions,
        'all-initiatives': task.all_initiatives,
        'all-references': task.all_references,
        'all-votes': task.all_votes,
        'all-interventions': task.all_interventions,
        'single-initiative': task.single_initiatives,
        'single-intervention': task.single_interventions,
        'single-vote': task.single_votes,
        'type-initiative': task.type_initiatives,
        'type-references': task.type_references,
        'type-interventions': task.type_interventions,
        'type-votes': task.type_votes,
        'type-all-initiative': task.type_all_initiatives,
        'type-all-references': task.type_all_references,
        'type-all-interventions': task.type_all_interventions,
        'type-all-votes': task.type_all_votes,
        'members': task.members,
        'default': task.run
    }
    run_command(subcommands, args)

commands = {
    'alerts': send_alerts,
    'tagger': tag,
    'untagger': untag,
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
