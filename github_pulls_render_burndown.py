#!/usr/bin/python
# encoding: utf8

from json import load, dump
from cgi import escape
from datetime import datetime

# Render data
with open('/tmp/github-pulls.json') as f_in:
    data = load(f_in)

    # Hacky numerical sort for our release numbering scheme
    milestones = data.keys()
    milestones = [[int(i) for i in m.split('.')] for m in milestones if m != 'Unassigned']
    milestones.sort()
    milestones = [u'.'.join(map(str,m)) for m in milestones if m != 'Unassigned']

    print('# Quattor Backlog')

    for milestone in milestones:
        print "\n## " + milestone.title()
        repos = data[milestone].keys()
        to_burn = 0
        burned = []

        for repo in repos:
            things = data[milestone][repo]['things']
            if things:
                for t in things:
                    to_burn += 1
                    if 'closed' in t:
                        burned.append(t['closed'])

        burned.sort()

        bdata = {
            'to_burn': to_burn,
            'closed': [],
        }
        for t in burned:
            to_burn -= 1
            bdata['closed'].append([t, to_burn])

        dump(bdata, open('burndown-%s.json' % milestone, 'w'))
