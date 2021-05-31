# tipi-engine
Motor de tareas y procesos internos de Tipi

## Requirements
Install setup and it will install all dependencies and libraries
```
./setup.sh
```

## Configuration

All variables are in .env file


Init Luigi
=======
Inside Virtualenv:
```
./base.py
```
or exec cron.sh
```
./cron.sh
```

Add to Crontab /etc/crontab
=======
```
0 2	*/3 * * root	bash /path/to/cron.sh
```

Reset Denylist
=======
Access to redis-cli and flush:
```
flushall
```
If you want only flush a specific db:
```
select [number db]
flushdb
```

Available Commands
=======

## Extractor
- `python quickex.py extractor initiatives`: Extracts new initiatives.
- `python quickex.py extractor references`: Calculates references that are not present in the database and prints them.
- `python quickex.py extractor votes`: Extracts new votes.
- `python quickex.py extractor interventions`: Extracts new video interventions.
- `python quickex.py extractor all-initiatives`: Extracts all the initiatives.
- `python quickex.py extractor all-references`: Calculates all the references.
- `python quickex.py extractor all-votes`: Extracts all the votes.
- `python quickex.py extractor all-interventions`: Extracts all the video interventions
- `python quickex.py extractor single-initiative [initiative reference]`: Extracts a single initiative.
- `python quickex.py extractor single-intervention [initiative reference]`: Extracts the video interventions of a single reference.
- `python quickex.py extractor single-vote [initiative reference]`: Extracts the votes of a single reference.
- `python quickex.py extractor type-initiative [initiative code]`: Extracts all the new initiatives of the specified initiative type.
- `python quickex.py extractor type-references`: Prints all the new initiatives of the specified initiative type.
- `python quickex.py extractor type-interventions`: Extracts all the video interventions of the new initiatives of the specified initiative type.
- `python quickex.py extractor type-votes`: Extracts all the votes of the new initiatives of the specified initiative type.
- `python quickex.py extractor type-all-initiative [initiative code]`: Extracts all the initiatives of the specified initiative type.
- `python quickex.py extractor type-all-references`: Prints all the initiatives of the specified initiative type.
- `python quickex.py extractor type-all-interventions`: Extracts all the video interventions of the initiatives of the specified initiative type.
- `python quickex.py extractor type-all-votes`: Extracts all the votes of the initiatives of the specified initiative type.
- `python quickex.py extractor members`: Extracts all the members and updates the existing ones in the DB.

## Tagger
- `python quickex.py tagger all` (default): Tags all the initiatives with all the tags and topics.
- `python quickex.py tagger new-tag [TAG]`: Tags all the initiatives with the tag specified. Must be already present in the topics dictionary.
- `python quickex.py tagger new-topic [TOPIC]`: Tags all the initiatives with the all tags of the specified topic. Must be already present in the topic dictionary.
- `python quickex.py tagger modify-regex [TAG]`: Finds the tag and removes it from all initiatives and tags all the initiatives using the updated regex. The regex must be updated in the topic dictionary.
- `python quickex.py tagger rename-tag [TAG]`: Finds all the occurrences of the specified tag in all the initiatives and replace it with the new name.

# Untagger
- `python quickex.py untagger all` (default): Marks all initiatives as not tagged.
- `python quickex.py untagger undo`: Marks all initiatives as tagged.
- `python quickex.py untagger topic "[TOPIC]"`: Marks all initiatives with the given topic as untagged.
- `python quickex.py untagger tag "[TAG]"`: Marks all initiatives with the given tag as untagged.
- `python quickex.py untagger remove-topic [TOPIC]`: Removes the given topic from all initiatives.
- `python quickex.py untagger remove-tag [TAG]`: Removes the given tag from all the initiatives.
