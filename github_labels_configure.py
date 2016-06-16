#!/usr/bin/python

from github import Github
from json import dump
from datetime import date, datetime, timedelta
from calendar import monthrange
from itertools import ifilter

from github_release_config import *

g = Github(USERNAME, OAUTH_TOKEN)
q = g.get_user(ORGANISATION)

# Requires the dictionary STANDARD_LABELS = { label: hexcolor } to be defined in github_release_config

# Collect data
for r in REPOS:
    print r
    repo = q.get_repo(r)
    labels = repo.get_labels()
    existing_labels = {}

    for label in labels:
        existing_labels[label.name] = label

    for label, color in STANDARD_LABELS.iteritems():
        if label in existing_labels:
            if existing_labels[label].color != color:
                existing_labels[label].edit(label, color)
                print "    Updated %s : %s" % (label, color)
        else:
            repo.create_label(label, color)
            print "    Added %s : %s" % (label, color)

    print # Seperator
