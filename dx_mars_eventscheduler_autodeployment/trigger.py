#!python2.7

import sys
import os
import shlex
import json
import subprocess as sb
import re

# sys.path.append('./cqm')
sys.path.append(os.getcwd())
from cqm_libs.utility import utility
from cqm_libs.artefactory import artefactory
from cqm_libs.jira import jira

JIRAKEY = os.getenv("JIRAKEY", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
WORKSPACE = os.getenv("WORKSPACE", None)
JIRASERVER = "http://10.33.20.21:8080/jira"

SERVICE = None
TYPE = None
ENVIRONMENT = None

filename = None


JIRA = jira(server=JIRASERVER, userName=JIRAUSER, password=JIRAPASS)
arr1 = ['fields.issuetype.id']
arr2 = ['issuetype']
fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

print fields["issuetype"]

## build eventscheduler
if int(fields["issuetype"]) == 11303:
	arr1 = ['fields.customfield_13008.value']
	arr2 = ['branch']
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	SERVICE = "eventscheduler"
	TYPE = "build"
	ENVIRONMENT = "CI"
	BRANCH = str(fields["branch"])
	
	filename = "DX-MARS_Build_eventscheduler.properties"

	jsonDic = {}
	jsonDic['_TYPE']=TYPE
	jsonDic['_SERVICE']=SERVICE
	jsonDic['SERVICE'] = SERVICE
	jsonDic['JIRAKEY'] = JIRAKEY
	jsonDic['BRANCH'] = BRANCH

	print jsonDic



    
# deploy    
elif int(fields["issuetype"]) == 11406:
	
	arr1 = ['fields.customfield_13008.value','fields.customfield_13007.child.value', 'fields.customfield_13102.value' ]
	arr2 = ['branch', 'rc', 'environment' ]
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	SERVICE = "eventscheduler"
	ENVIRONMENT = str(fields["environment"])
	BRANCH = str(fields['branch'])
	RC = str(fields['rc'])
	TYPE = "deploy"
	
	filename = "DX-MARS_Deploy_eventscheduler.properties"


	jsonDic = {}
	jsonDic['SERVICE'] = SERVICE
	jsonDic['JIRAKEY'] = JIRAKEY
	jsonDic['ENVIRONMENT'] = ENVIRONMENT
	jsonDic['_TYPE']=TYPE
	jsonDic['_SERVICE']=SERVICE
	jsonDic['_ENVIRONMENT']=ENVIRONMENT
	jsonDic['_RC']= RC
	jsonDic['RC']= RC
	jsonDic['BRANCH'] = BRANCH

   

	print jsonDic
    

# promote
elif int(fields["issuetype"]) == 11405:
	arr1 = ['fields.customfield_13008.value','fields.customfield_13007.value' ]
	arr2 = ['branch', 'rc' ]
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	TYPE = "promote"
	SERVICE = "eventscheduler"
	RC = str(fields['rc'])

	jsonDic = {}
	jsonDic['SERVICE'] = SERVICE
	jsonDic['RC'] = RC
	jsonDic['_TYPE']=TYPE
	jsonDic['_SERVICE']=SERVICE
	jsonDic['_RC']= RC
	jsonDic['JIRAKEY'] = JIRAKEY

	filename = "DX-MARS_Promote_eventscheduler.properties"

	print jsonDic

	



else:
	print "No such issue type"
	exit (1)

if filename is not None:
	with open(filename, 'w') as myFile:
		for key in jsonDic.keys():
			print 'key='+key
			print >>myFile,key+'='+jsonDic[key]
		myFile.close()	