#!/usr/bin/python
# encoding: utf8

from github import Github, GithubException
from json import dump
from sys import stdout
from collections import namedtuple
from itertools import chain
from ssl import SSLError
from datetime import datetime, timedelta
import socket
from re import compile, IGNORECASE

RE_DEPENDS = compile(r'((?:depends|based) on|requires)\s+(?P<repository>[\w/-]*)#(?P<number>\d+)', IGNORECASE)
RE_FIXES = compile(r'(close[sd]?|fix(?:e[sd])?|resolve[sd]?)', IGNORECASE)

from github_release_config import *

g = Github(USERNAME, OAUTH_TOKEN)
g = g.get_user(ORGANISATION)

data = {}
relationships = []

MockMilestone = namedtuple('Milestone', ['title', 'open_issues', 'closed_issues', 'due_on'])
backlog = MockMilestone(title='Backlog', open_issues=0, closed_issues=0, due_on=None)

# Collect data
for repo_name in REPOS:
    repo = g.get_repo(repo_name)
    stdout.write("    %-32s" % (repo.name))

    retries = 3
    while retries:
        try:
            milestones = repo.get_milestones(state='open')

            for milestone in chain(milestones, [backlog]):
                if milestone.title not in data:
                    data[milestone.title] = {}

                if repo.name not in data[milestone.title]:
                    data[milestone.title][repo.name] = {'things': [], 'closed': 0, 'open': 0, 'due': None}

                data[milestone.title][repo.name]['open'] += int(milestone.open_issues)
                data[milestone.title][repo.name]['closed'] += int(milestone.closed_issues)

                if milestone.due_on:
                    data[milestone.title][repo.name]['due'] = milestone.due_on.isoformat()

                stdout.write('█')
                stdout.flush()

            break

        except (SSLError, socket.error) as e:
            stdout.write('R')
            retries -= 1

    try:
        retries = 3
        while retries:
            try:
                # We care about all things that are assigned to a milestone, or things from the last 60 days that are not assigned to a milestone
                things_all_milestones = repo.get_issues(state='all', milestone='*')
                things_backlog = repo.get_issues(milestone='none', since=datetime.now() - timedelta(days=60))
                things = chain(things_all_milestones, things_backlog)

                for t in things:
                    stdout.write('▒')
                    stdout.flush()
                    milestone_name = 'Backlog'
                    if t.milestone:
                        milestone_name = t.milestone.title

                    if milestone_name in data: # Skip any issues belonging to milestones that have been closed already
                        if repo.name in data[milestone_name]:
                            this_thing = {
                                'number' : t.number,
                                'url' : t.html_url,
                                'title' : t.title,
                                'user' : t.user.login,
                                'assignee' : t.assignee.login if t.assignee != None else None,
                                'created' :  t.created_at.isoformat(),
                                'updated' :  t.updated_at.isoformat(),
                                'state' : t.state,
                                'comment_count' : t.comments,
                                'labels' : [],
                            }

                            this_thing['type'] = 'issue'
                            if t.pull_request:
                                this_thing['type'] = 'pull-request'
                                this_thing['labels'] = [l.name for l in t.labels]
                                pr = repo.get_pull(t.number)

                            this_thing['labels'] = [l.name for l in t.labels]

                            if t.closed_at:
                                this_thing['closed'] = t.closed_at.isoformat()

                            data[milestone_name][repo.name]['things'].append(this_thing)

                            dependencies = RE_DEPENDS.search(t.body)
                            if dependencies:
                                dep_repo = dependencies.group('repository')
                                if not dep_repo:
                                    dep_repo = repo.name
                                relationships.append(('%s/%s' % (repo.name, t.number), 'requires', '%s/%s' % (repo.name, dependencies.group('number'))))
                        else:
                            print "\nWARNING: Dropped thing %d (%s) from repo %s (missing milestone?)" % (t.number, t.title ,repo.name)
                break

            except SSLError:
                stdout.write('R')
                retries -= 1

    except GithubException as e:
        print 'ERROR: %(message)s' % e

    print

with open('/tmp/github-pulls.json', 'w') as f:
    dump(data, f, indent=4)

with open('/tmp/github-pulls-relationships.json', 'w') as f:
    dump(relationships, f, indent=4)
