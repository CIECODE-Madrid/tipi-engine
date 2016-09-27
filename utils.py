import os

FILES = [
    'scrap.tmp',
    'labeling.tmp',
    'alerts.tmp',
    ]

def clean_files():
    for file in FILES:
        os.remove(file)
