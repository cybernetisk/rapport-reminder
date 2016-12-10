#!/usr/bin/env python
# coding=utf-8
from settings import *

from jira import JIRA
import markdown
import codecs

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to, subject, message):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'arkiv@cyb.no'
    msg['To'] = to
    msg.attach(MIMEText(message, 'html', 'utf-8'))
    s = smtplib.SMTP('localhost')
    s.sendmail('arkiv@cyb.no', to, msg.as_string())
    s.close()


def create_message(issues, mal):
    mdstr = ''
    for issue in issues:
        mdstr = mdstr + '* [%s](%s)\n' % (issue.fields.summary, 'https://jira.cyb.no/browse/%s' % str(issue))

    return mal % (issues[0].fields.assignee, mdstr)


def map_issues_to_email(issues):
    users = dict()
    for issue in issues:
        assignee = issue.fields.assignee
        if assignee is not None:
            if assignee.emailAddress in users:
                users.get(assignee.emailAddress).append(issue)
            else:
                users[assignee.emailAddress] = [issue, ]

    return users


# Login to Jira
jira = JIRA(JIRA_URL, basic_auth=(JIRA_USER, JIRA_PW))

# Get up to 500 issues in prosject RAP that is not done.
issues = jira.search_issues('project=RAP AND status!=DONE', maxResults=500)

users = map_issues_to_email(issues)

# get the mail from file
fil = codecs.open('mailmal.md', 'r', encoding='utf-8')
mal = fil.read()
fil.close()

# send emails
for emails, issues in users.items():
    send_email(emails, 'Rapporter CYB', markdown.markdown(create_message(issues, mal), output_format='HTML5'))
