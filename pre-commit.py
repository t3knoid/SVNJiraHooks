# This Python script will prevent check-ins with an invalid commit message. 
# A commit message consist of a Jira ticket ID followed by the actual 
# commit message. It also checks if a Jira issue has a Fix Version set.
# It also ensures that the issue status is In Progress.

import os
import sys
import xmlrpclib
import requests
import re

# Specify Jira properties here
BaseURL = ''
Login = ''
Password = ''

# configure svnlook path
svnlookPath = '"C:\\Program Files (x86)\\VisualSVN Server\\bin\\svnlook.exe"'

# get committer
try:
    f = os.popen(svnlookPath + ' author ' + sys.argv[1] + ' --transaction ' + sys.argv[2])
    committer = f.read()
    if f.close():
        raise 1
    committer = committer.rstrip("\n\r")
except:
    print >> sys.stderr, 'Unable to get committer with svnlook.'
    sys.exit(1)

# get commit message
try:
    f = os.popen(svnlookPath + ' log ' + sys.argv[1] + ' --transaction ' + sys.argv[2])
    commitMessage = f.read()
    if f.close():
        raise 1
    commitMessage = commitMessage.rstrip('\n\r')
except:
    print >> sys.stderr, 'Unable to get commit message with svnlook.'
    sys.exit(1)

# Reject commit if commit message is empty
if not commitMessage:
    print >> sys.stderr, 'Commit rejected: Commit message is empty'
    sys.exit(1)

# print arguments
print >> sys.stderr, 'Committer: ' + committer
print >> sys.stderr, 'Commit message: "' + commitMessage + '"'

# check if TortoiseSVN autocommit
if commitMessage.startswith("TortoiseSVN auto commit:"):
    print >> sys.stderr, 'Commit accepted.'
    sys.exit(0)

# Parse issue from commit message
word = re.split('[ :]', commitMessage)
jiraIssue = word[0]

# Use REST to access Jira issue fields
# Document is returned in JSON format
try:
    queryURL = jiraserver.BaseURL + '/rest/api/latest/issue/' + jiraIssue
    req = requests.get(queryURL,
                       auth=(jiraserver.Login, jiraserver.Password),
                       headers={
                               'X-Atlassian-Token': 'no-check',
                               'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'Cache-Control': 'no-cache',
                               }
                       )
    # Check if status is OK
    if req.status_code == 200:
            data = req.json()  # data holds JSON document
    else:
        raise Exception("An error occurred while performing the request. Error code (%s) was returned." % req.status_code)
except Exception as ex:
    print >> sys.stderr, ex
    sys.exit(1)

# Fail commit if issue is not "In Progress"
jiraStatus = data['fields']['status'].get('name')  # Read status field from returned JSON document
if jiraStatus != 'In Progress' : # Exit immediately if Jira issue status is not In Progress
    print >> sys.stderr, 'Commit rejected: Issue %s is not in progress. Status is currently %s. Modify the Jira status to In Progress and try committing again.' % (jiraIssue,jiraStatus)
    sys.exit(1)

# Fail commit if Fix Version field is empty.
try:
    # Get Fix Version info from Jira
    # Fix Version is an array. Use an exception handler
    # to check if this array is empty.
    jiraFixedVersion = data['fields']['fixVersions'][0].get('name')  # Read fixVersion field from returned JSON document
except IndexError as ex:
    print >> sys.stderr, 'Commit rejected: Issue %s has no Fix Version set. Set a value to the Fix Version field and try committing again.' % jiraIssue # fail commit
    sys.exit(1)

