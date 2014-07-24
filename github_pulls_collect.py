#!/usr/bin/python
# encoding: utf8

from github import Github, GithubException
from json import dump
from sys import stdout
from collections import namedtuple
from itertools import chain
from ssl import SSLError

from quattor_release_config import *

g = Github(USERNAME, OAUTH_TOKEN)
g = g.get_user(ORGANISATION)

data = {}

MockMilestone = namedtuple('Milestone', ['title', 'open_issues', 'closed_issues', 'due_on'])
unassigned = MockMilestone(title='Unassigned', open_issues=0, closed_issues=0, due_on=None)

# Collect data
for repo_name in REPOS:
    repo = g.get_repo(repo_name)
    stdout.write("    %-32s" % (repo.name))

    retries = 3
    while retries:
        try:
            milestones = repo.get_milestones()

            for milestone in chain(milestones, [unassigned]):
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

        except SSLError:
            stdout.write('R')
            retries -= 1

    try:
        retries = 3
        while retries:
            try:
                #things = repo.get_issues(state='all')
                things = repo.get_issues()

                for t in things:
                    stdout.write('▒')
                    stdout.flush()
                    milestone_name = 'Unassigned'
                    if t.milestone:
                        milestone_name = t.milestone.title
        
                    if milestone_name in data: # Skip any issues belonging to milestones that have been closed already
                        if repo.name in data[milestone_name]:
                            icon = 'issue-opened'
                            if t.pull_request:
                                icon = 'git-pull-request'
        
                            data[milestone_name][repo.name]['things'].append({
                                'number' : t.number,
                                'url' : t.html_url,
                                'title' : t.title,
                                'icon': icon,
                                'user' : t.user.login,
                                'created' :  t.created_at.isoformat(),
                                'updated' :  t.updated_at.isoformat(),
                                'state' : t.state,
                                'comment_count' : t.comments,
                            })
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
