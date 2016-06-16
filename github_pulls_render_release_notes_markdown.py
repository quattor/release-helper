#!/usr/bin/python
# encoding: utf8

from json import load
from cgi import escape
from datetime import datetime
from web import template
from argparse import ArgumentParser

TEMPLATE = '''$def with (milestone, notes, issues, pulls, backwards_incompatible)

---
layout: article
title: Quattor $milestone.0 released
category: news
author: James Adams
---

Packages are available from our [yum repository](http://yum.quattor.org/$milestone.0/), both the RPMs and the repository metadata are signed with [my GPG key](http://yum.quattor.org/GPG/RPM-GPG-KEY-quattor-jrha).

As always, many thanks to everyone who contributed! We merged $pulls pull requests and resolved $issues issues.

The next release should be NEXT.0, take a look at the [backlog](http://www.quattor.org/release/) to see what we're working on.


Backwards Incompatible Changes
------------------------------

$for repo, prs in backwards_incompatible.iteritems():
    $if prs:
        ### $repo
        $for id, title, labels in prs:
            $if ': ' in title:
                $code:
                    title = '**' + title.replace(': ', ':** ', 1)
            * [$title](https://github.com/quattor/$repo/pull/$id)
        $# Blank line to seperate sections
Changelog
---------

$for repo, prs in notes.iteritems():
    ### $repo
    $for id, title, labels in prs:
        $if ': ' in title:
            $code:
                title = '**' + title.replace(': ', ':** ', 1)
        * [$title](https://github.com/quattor/$repo/pull/$id)
    $# Blank line to seperate sections
'''

RENDER = template.Template(TEMPLATE)

parser = ArgumentParser(description='Generate release notes.')
parser.add_argument('milestone', metavar='M', help='Milestone associated with this release.')
args = parser.parse_args()

notes = {}
backwards_incompatible = {}

# Render data
with open('/tmp/github-pulls.json') as f_in:
    data = load(f_in)
    
    milestone = args.milestone
    repos = data[milestone].keys()
    repos.sort()
    count_issues = 0
    count_pulls = 0
    for repo in repos:
        count_issues += len([t for t in data[milestone][repo]['things'] if t['type'] == 'issue'])
        things = [t for t in data[milestone][repo]['things'] if t['type'] == 'pull-request']
        count_pulls += len(things)
        if things:
            notes[repo] = [(t['number'], t['title'], t['labels']) for t in things]
            notes[repo].sort(key=lambda t: t[1])
            backwards_incompatible[repo] = [n for n in notes[repo] if 'backwards incompatible' in n[2]]

print RENDER(milestone, notes, count_issues, count_pulls, backwards_incompatible)
