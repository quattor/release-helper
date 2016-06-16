#!/usr/bin/python
# encoding: utf8
# vi:ts=4:et

from json import load
from cgi import escape
from datetime import datetime
from web import template
from argparse import ArgumentParser

render = template.render('templates')

notes = {}

# Render data
with open('/tmp/github-pulls.json') as f_in:
    data = load(f_in)

    milestones = data.keys()
    milestones.sort()
    for milestone in milestones:
        repos = data[milestone].keys()
        repos.sort()
        for repo in repos:
            things = [t for t in data[milestone][repo]['things']]
            if things:
                if repo not in notes:
                    notes[repo] = []
                notes[repo] = notes[repo] + [t for t in things if 'discuss at workshop' in t['labels']]


print render.to_discuss(notes)
