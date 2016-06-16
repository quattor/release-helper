#!/usr/bin/python

from github import Github
from json import dump
from datetime import date, datetime, timedelta
from calendar import monthrange
from itertools import ifilter
import argparse

from github_release_config import *

g = Github(USERNAME, OAUTH_TOKEN)
q = g.get_user(ORGANISATION)

data = {}

parser = argparse.ArgumentParser()
parser.add_argument('--create', metavar='MILESTONE', type=str)
parser.add_argument('--close', metavar='MILESTONE', type=str)
args = parser.parse_args()

#import sys
#sys.exit()

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
    m_open = repo.get_milestones(state='open')
    m_closed = repo.get_milestones(state='closed')
    m_all = []

    print '  Closed'
    for m in m_closed:
        print '    %s' % m.title
        m_all.append(m.title)
        if m.due_on >= datetime.now() - timedelta(1):
            m.edit(m.title, state='open')
            print '        Opening'

    print '  Open'
    for m in m_open:
        print '    %s' % m.title
        m_all.append(m.title)
        release = m.title.split('.')
        if len(release) == 2:
            if m.title == '16.4':
                m.edit(m.title, due_on=date(2016, 5, 20))
                print '        Pushed back due date for 16.4'

            if m.due_on:
                if m.due_on < datetime.now() - timedelta(1):
                    m.edit(m.title, state='closed')
                    print '        Closing'
            else:
                year = int('20' + release[0])
                month = int(release[1])
                day = monthrange(year, month)[-1]
                m.edit(m.title, due_on=date(year, month, day))
                print '        Updated due date'

        else:
            print '        Point release, will not modify'

    #print '  Checking future milestones'
    #for year, month in m_future:
    #    n = "%d.%d" % (year-2000, month)
    #    if n not in m_all:
    #        print '    %s not found - creating' % n
    #        day = monthrange(year, month)[-1]
    #        repo.create_milestone(title=n, due_on=date(year, month, day))

    print # Seperator


with open('/tmp/github-milestones.json', 'w') as f:
    dump(data, f)
