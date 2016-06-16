#!/usr/bin/python

from github import Github
from json import dump
from datetime import date, datetime, timedelta
from calendar import monthrange
from itertools import ifilter

from github_release_config import *

g = Github(USERNAME, OAUTH_TOKEN)
q = g.get_user(ORGANISATION)

data = {}

today = date.today()
month = today.month

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day, monthrange(year,month)[1])
    return date(year, month, day)

# Ensure we have an even numbered month!
if month % 2 > 0:
    month += 1

today = date(today.year, month, 1)

m_future = []
for m in range(1, 4):
    n = add_months(today, m*2)
    m_future.append((n.year, n.month))
del today

# Collect data
for r in REPOS:
    print r
    repo = q.get_repo(r)
    data[r] = []
    m_open = repo.get_milestones(state='open', sort='due_date', direction='desc')
    m_all = []

    print '  Open'
    for m in m_open:
        print '    %s' % m.title
        m_all.append(m.title)
        release = m.title.split('.')
        if len(release) == 2:
            year = int('20' + release[0])
            month = int(release[1])
            day = monthrange(year, month)[-1]

            due_original = date(year, month, day)
            due_updated = add_months(due_original, 2)
            title_updated = '{0:%y}.{0.month}'.format(due_updated)

            print '        New Title %s' % title_updated
            print '          Was Due %s' % due_original
            print '          Now Due %s' % due_updated
            m.edit(title_updated, due_on=due_updated) # DANGER!
            print '        Updated'
        else:
            print '        Point release, will not modify'

    print # Seperator


with open('/tmp/github-milestones.json', 'w') as f:
    dump(data, f)
