# This script reads a properties file
# and derives the version information
# from the file. The version information
# is the first line of the file.
#
# The following assumption is made about
# the repository structure:
#
# -\ProjectName\
#              \trunk
#              \branches
#              \tags

import os
import sys
import svn.remote
import re

svnlookPath = '"C:\\Program Files (x86)\\VisualSVN Server\\bin\\svnlook.exe"'
svnrepoURL = 'http://svnserver/svn/TestRepo/'
svnUsername = 'svn'
svnPassword = 'svn2011'
try:
    f = os.popen(svnlookPath + ' changed ' + sys.argv[1] + ' --transaction ' + sys.argv[2])
    changed = f.read()
    if f.close():
        raise 1
    output = re.split("\n", changed)  # Break up output into a list of lines
except:
    print >> sys.stderr, 'Unable to get svnlook changed information.'
    sys.exit(1)

# Get information from svnlook changed command
line = re.split(" ", output[0])  # work on first line output
operation = line[0]  # Operation performed by user
svnpath = line[3].rstrip('\n\r')  # Path to changed file
svnpath_list = svnpath.split('/')  # split the path to changed file
project_name = svnpath_list[0]  # first item in list is the project name
trunk_branch = svnpath_list[1]  # second item identifies if its the trunk or branch
svn_projectroot_path = svnrepoURL + '/' + project_name + '/' + trunk_branch + '/'

# Get version information of Trunk or Branch
# parsing out property values located in teamcity.default.properties
# located in root of Stroz Discovery solution folder
try:
    remotesvn = svn.remote.RemoteClient(svn_projectroot_path,
                                        username=svnUsername,
                                        password=svnPassword)   # Connect to remove SVN Server
    properties=remotesvn.cat('teamcity.default.properties')  # Get content of teamcity.default.properties
    lines = re.split("\n", properties)  # Break up output into a list of lines
    propertyLine = re.split("=", lines[0])  # First line contains env.Version= property
    version = propertyLine[1].strip(' \n\r')  # Second element contains version value
except Exception as ex:
    print >> sys.stderr, ex
    sys.exit(1)
