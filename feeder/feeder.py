#!/usr/sbin/python2.6

import sys
import base64
import shlex
import os
import urllib2
import json
import re
from string import maketrans, translate
import subprocess as sb
import time
import datetime
import mysql.connector as mysql
import urllib
import collections


global cur, conn, MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_DB

MYSQL_DB = "cqmdb";
MYSQL_HOST = "10.33.20.13"
MYSQL_USER = "root"
MYSQL_PASS = "Purple5967Table!"

conn = mysql.Connect(user=MYSQL_USER, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_DB)
cur = conn.cursor()


global SONAR_URL, SONAR_USER, SONAR_PASSWORD
SONAR_URL="/api/resources?resource="
SONAR_USER="admin"
SONAR_PASSWORD="admin"


global SVN_USER, SVN_PASS
SVN_USER="CQMSVN"
SVN_PASS="K_29^ob"

global ARTIUSER, ARTIPASS
ARTIUSER = "admin"
ARTIPASS = "K_29^ob"



class Version(object):
	Id = None # id in database
	VersionName = None
	VersionId = None # id in jira api
	JiraKey = None
	StatusId = None
	Summary = None
	EstimatedTime = None
	TimeSpent = None
	Progress = None
	Total = None
	Percent = None
	ReleaseDate = None


class Issue(object):
	DashBoardId = None
	Summary = None
	JiraKey = None
	Labels = None


class JenkinsBuild(object)	:
	JobId = None
	BuildId = None
	StartTime = None
	Duration = None
	Status = None
	Environment = ""
	Type = ""
	Service = ""
	RC = ""
	JiraKey = ""

def sortByDate(array):
  return array[1]


def getListFiles(_artifactory_server, _folder = "", _iffile = False):
  global ARTIUSER, ARTIPASS, artifactory_server
  artifactory_server = _artifactory_server
  if _folder == None:
    _folder = ""
# curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
  
  command_curl_get_list = "curl -D- -X GET -u " + ARTIUSER + ":" + ARTIPASS + " " + str(artifactory_server) + str(_folder) + "/" 
  # print command_curl_get_list
  curl_get_list = sb.Popen(shlex.split(command_curl_get_list), stdout=sb.PIPE)
  data_curl_get_list = curl_get_list.communicate()[0]

  # data_curl_get_list = getJson(artifactory_server + str(_folder) + "/", [ARTIUSER, ARTIPASS])
  # print json.loads(json.dumps(data_curl_get_list))

  if _iffile:
    # print data_curl_get_list
    return json.loads(json.dumps(data_curl_get_list))
  # print data_curl_get_list
  # data_curl_get_list = curl_get_list.stdout.read()
  p = re.compile(ur'({.*})', re.DOTALL)
  group = re.search(p, str(data_curl_get_list))
  try:
  	print group.groups()
  except AttributeError:
  	print "group is empty"



  # group = json.loads(json.dumps(data_curl_get_list))

  if group is not None:
    files = []
    # print group.groups()[0]
    data_json = json.loads(group.groups()[0])
    # data_json = group
    if "children" in data_json:
    	# print data_json
    	return data_json['children']
    else:
      # msg = "[ERROR] Artifactory " + _folder + " is empty or service not found"
      # print msg
      # mail.write(msg)
      # sys.exit(-1)
      return []


def getLastPromote(_artifactory_server):
  listFiles = []
  folders = getListFiles(_artifactory_server)
  if folders is not None:
	  for folder in folders:
	    if folder['folder'] == True and folder['uri'] not in ['/LIVE', '/trunk', '/.index']:
	      files = getListFiles(_artifactory_server,folder['uri'][1:])
	      for f in files:
	        # print folder['uri']
	        print f
	        f2 = folder['uri'][1:] + f['uri']
	        # print f2
	        print getListFiles(_artifactory_server,f2, True)
	        data = "\n".join((getListFiles(_artifactory_server,f2, True).split("\n")[7:]))
	        lastUpdated = json.loads(data)['lastUpdated']
	        listFiles.append([f2, lastUpdated])


  return sorted(listFiles, key = sortByDate, reverse = True)[:5]



def getJson(_url, _auth = None):
	# _url = urllib.urlretrieve(_url)
	#req = urllib2.Request(urllib2.unquote(urllib2.quote(_url.encode("utf8"))))

	try:
		req = urllib2.Request(_url)
		# print _url
		if _auth is not None and _auth[0] != "" and _auth[1] != "":
			auth = "Basic " + base64.b64encode(_auth[0] + ":" + _auth[1])
			req.add_header("Authorization", auth)
		resp = None
		resp = urllib2.urlopen(req).read()

		if json.loads(resp) != None:
			return json.loads(resp)
		return json.loads(json.dumps(resp))
	except urllib2.HTTPError, e:
		print "Error: " + _url
		print e
	except urllib2.URLError, e:
		print "Error: " + _url
		print e
	except ValueError:
		print "Error: " + _url
		print e


def getJiraLatestSprint(_dashboard):
	data = getJson("http://10.33.20.21:8080/jira/rest/greenhopper/latest/sprintquery/" + str(_dashboard), ['cqm_test1', 'cqmtest'])
	sprintId = 0
	sprintName = ""
	if data is not None and "sprints" in data:
		for sprint in data['sprints']:
			if sprint['id'] > sprintId and sprint['state'] == "ACTIVE":
				sprintId = sprint['id']
				sprintName = sprint['name']

		return (sprintId, sprintName)
	return (0,0)


def getClosedIssues(_sprint, _auth = None):
	tmp = getJson("http://10.33.20.21:8080/jira/rest/api/2/search?jql=Sprint=" + str(_sprint) + "+AND+status+in+(Resolved,+Closed,+Close)+AND+issuetype+!=+Sub-task&maxResults=0", _auth )
	if tmp is not None:
		return tmp['total']
	else:
		return 0


def getTotalIssues(_sprint, _auth = None):
	# return getJson("https://tools.ladbrokes.com/jira/rest/api/2/search?jql=Sprint=" + str(_sprint) + "&maxResults=0", _auth )['total']

	tmp = getJson("http://10.33.20.21:8080/jira/rest/api/2/search?jql=Sprint=" + str(_sprint) + "+AND+issuetype+!=+Sub-task&maxResults=0", _auth )
	if tmp is not None:
		return tmp['total']
	else:
		return 0

def getInProgressIssues(_sprint, _auth = None):
	# print getJson("https://tools.ladbrokes.com/jira/rest/api/2/search?jql=Sprint=" + str(_sprint) + "+AND+status+in+%28%27In+Dev%27,+%27In+Progress%27%29&maxResults=0", _auth )['total']
	# return getJson("https://tools.ladbrokes.com/jira/rest/api/2/search?jql=Sprint=" + str(_sprint) + "+AND+status+in+%28%27In+Dev%27,+%27In+Progress%27%29&maxResults=0", _auth )['total']
	subjson = getJson("http://10.33.20.21:8080/jira/rest/api/2/search?jql=Sprint=" + str(_sprint) + "+AND+status+in+%28%27In+Dev%27,+%27In+Progress%27%29+AND+issuetype+!=+Sub-task", _auth )
	if subjson is not None:

		issues = []

		if "issues" in subjson:
			for entry in subjson['issues']:
				issue = Issue()
				issue.Summary = str(entry['fields']['summary']).replace("'", "&#39;")
				issue.JiraKey = str(entry['key'])
				issue.Labels = str(",".join(entry['fields']['labels'])).replace("'", "&#39;")
				issues.append(issue)


		# return subjson['total'], subjson['issues']
		return subjson['total'], issues
	else:
		return 0,0


def getJiraSprintDetails(_dashboard, _sprint):
	data = getJson("http://10.33.20.21:8080/jira/rest/greenhopper/latest/rapid/charts/sprintreport?rapidViewId=" + str(_dashboard) + "&sprintId=" + str(_sprint), ['cqm_test1', 'cqmtest'])
	if data is not None:
		startDate = data['sprint']['startDate']
		endDate = data['sprint']['endDate']

		_auth = ['cqm_test1', 'cqmtest']
		totalIssues = getTotalIssues(_sprint, _auth)
		closedIssues = getClosedIssues(_sprint, _auth)
		
		inprogressIssues, issuesInProgress = getInProgressIssues(_sprint, _auth)


		return inprogressIssues, closedIssues, totalIssues, startDate, endDate, issuesInProgress
	else:
		return None


def getSVNData(_repo):

	command = "svn log " + _repo
	args = shlex.split(command)
	# file1 = open("svn.log", "wb")
	p = sb.Popen(args, stdout=sb.PIPE)
	data = p.communicate()[0]
	# file1.close()
	# time.sleep(1)

	# file1 = open("svn.log", "r")
	# data = file1.read()
	# file1.close()

	positions = []
	counter = 0
	dayBuilds = {}
	weekBuilds = {}
	monthBuilds = {}
	yearBuilds = {}
	allBuilds = 0
	dayContributers = {}
	contributers = []




	data2 = data.split(" | ")
	for m in xrange(1 , len(data2), 3):
		date = data2[m+1][0:10]
		month = date[0:7]
		year = date[0:4]
		contributer = data2[m]
		allBuilds += 1
		week = datetime.datetime.strptime(date, "%Y-%m-%d").isocalendar()[1]


		if date not in dayContributers:
			contributers = []
			contributers.append(contributer)
			dayContributers.update({date: contributers})
		else:
			contributers = []
			contributers = dayContributers[date]
			if contributer not in contributers:
				contributers.append(contributer)
				dayContributers.update({date: contributers})

		if date not in dayBuilds:
			dayBuilds.update({date : 1})
		else:
			counts = dayBuilds[date] + 1
			dayBuilds.update({date : counts})

		if week not in weekBuilds:
			weekBuilds.update({week: 1})
		else:
			counts = weekBuilds[week] + 1
			weekBuilds.update({week: counts})

		if month not in monthBuilds:
			monthBuilds.update({month : 1})
		else:
			counts = monthBuilds[month] + 1
			monthBuilds.update({month : counts})
		if year not in yearBuilds:
			yearBuilds.update({year:1})
		else:
			counts = yearBuilds[year] + 1
			yearBuilds.update({year: counts})

	# commits
	daily = allBuilds/len(dayBuilds)
	monthly = allBuilds/len(monthBuilds)
	annualy = allBuilds/len(yearBuilds)
	weekely = allBuilds/len(weekBuilds) 
	# biweekely = allBuilds/len(week)

	# today = time.strftime("%Y-%m-%d")
	# if today in dayContributers:
	# 	Contributers = ','.join(dayContributers[today])
	# 	CountContributers = len(dayContributers[today])
	# else:
	# 	Contributers = ""
	# 	CountContributers = 0

	


	return 	dayBuilds, weekBuilds, monthBuilds, yearBuilds, dayContributers
	# return daily, dayBuilds, monthly, monthBuilds, annualy, yearBuilds, CountContributers ,Contributers


def jenkinsRunningJobs(_jobname):
  command = "curl -X GET 'http://jira.ladbrokes.co.uk/jenkins/computer/api/json?tree=computer\[executors\[currentExecutable\[url\]\],oneOffExecutors\[currentExecutable\[\url\]\]\]&xpath=//url&wrapper=builds'"
  sb_cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
  data = sb_cmd.communicate()[0]
  json1 = json.loads(data)['computer']
  passed = True
  for entry in json1:
    for item in entry['executors']:
      if item['currentExecutable'] != None:
        if _jobname in item['currentExecutable']['url'].split("/"):
          passed = False
  				
  return not passed



def getJenkinsBuilds(_jenkinsproject, _jobname):
	# url = "http://jira.ladbrokes.co.uk/jenkins/view/CQM/job/" + _jobname + "/api/json?depth=1"
	url = "http://jira.ladbrokes.co.uk/jenkins/view/" + _jenkinsproject +  "/api/json?depth=2"
	data = getJson(url)
	jenkinsBuilds = []
	if data is not None and "jobs" in data and len(data['jobs']) > 0:
		for job in data['jobs']:
			if job['name'] == _jobname and job['name'] is not None:
				# print job['name']
				for entry in job['builds']:
					if entry['result'] == "SUCCESS":
						result = 1
					else:
						result = 0

					parameters = []
					for params in entry['actions']:
						if "parameters" in params:
							parameters = params['parameters']
							break

					jenkinsBuild = JenkinsBuild()
					jenkinsBuild.Duration = entry['duration']
					jenkinsBuild.StartTime = datetime.datetime.fromtimestamp((entry['timestamp']/1000)).strftime('%Y-%m-%d %H:%M:%S')
					jenkinsBuild.Status  = result
					jenkinsBuild.BuildId = entry['number']

					print parameters
					if parameters is not None and len(parameters) > 0:
						for param in parameters:


							print param
							if param['name'] == "_ENVIRONMENT":
								jenkinsBuild.Environment = str(param['value'])
							if param['name'] == "_TYPE":
								jenkinsBuild.Type = str(param['value'])
							if param['name'] == "_SERVICE":
								jenkinsBuild.Service = str(param['value'])
							if param['name'] == "_RC":
								jenkinsBuild.RC = str(param['value'])
							if param['name'] == "_JIRAKEY":
								jenkinsBuild.JiraKey = str(param['value'])

					jenkinsBuilds.append(jenkinsBuild)
	return jenkinsBuilds


def selectJenkinsJobs():
	sql = """
		SELECT 
			a.Project_Name, 
			b.Jenkins_Job_ID, 
			c.Jenkins_Job_Name 
		FROM CQM_Projects AS a 
		LEFT JOIN 
			Project_Jenkins_Jobs AS b ON a.Project_ID = b.Project_ID 
		LEFT JOIN 
			Jenkins_Jobs AS c ON c.Jenkins_Job_ID = b.Jenkins_Job_ID;

	"""

	global conn, cur
	cur.execute(sql)
	rows = cur.fetchall()
	return rows

def selectJenkinsJobStats():
	# sql = """
	# 	SELECT 
	# 		Jenkins_Job_ID, 
	# 		Jenkins_Build_ID 
	# 	FROM Jenkins_Job_Stats 
	# 	WHERE 
	# 		Jenkins_Build_ID IN 
	# 			(SELECT MAX(Jenkins_Build_ID) 
	# 			FROM 
	# 				Jenkins_Job_Stats t 
	# 			GROUP BY t.Jenkins_Job_ID);

	# """
	sql = """
		SELECT 
			Jenkins_Job_ID,
			MAX(Jenkins_Build_ID) 
		FROM 
			Jenkins_Job_Stats 
		GROUP BY Jenkins_Job_ID;
	"""

	global cur, conn
	cur.execute(sql)
	rows = cur.fetchall()
	return rows


# def insertJenkinsJobStats(_id, _packet):
def insertJenkinsJobStats(_jobId, _build):
	
	sql = """
		INSERT INTO Jenkins_Job_Stats 
		SET 
			Jenkins_Job_ID='{0}',
			Jenkins_Build_ID='{1}',
			Jenkins_Job_Start_Time='{2}',
			Jenkins_Job_Duration='{3}',
			Jenkins_Job_Status='{4}',
			Jenkins_Job_Environment='{5}',
			Jenkins_Job_Type='{6}',
			Jenkins_Job_Service='{7}',
			Jenkins_Job_RC='{8}',
			Jenkins_Job_JiraKey='{9}'
	""".format( _jobId, _build.BuildId, _build.StartTime, 
				_build.Duration, _build.Status, _build.Environment, 
				_build.Type, _build.Service, _build.RC, _build.JiraKey )

	print sql
	cur.execute(sql)
	conn.commit()

def getLogSvn(_repo, _rev):
	# command = "svn log " + _repo + " -r {" + str(datetime.date.today()) + "}"
	command = "svn log --non-interactive --username='{0}' --password='{1}' {2}".format(SVN_USER, SVN_PASS, _repo)
	if _rev != "":
		command = "svn log --non-interactive --username='{0}' --password='{1}' {2} -r HEAD:{3}".format(SVN_USER, SVN_PASS, _repo, _rev)

	# print command
	devnull = open(os.devnull, "wb")
	p = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=devnull)
	svn_data = p.communicate()[0]
	
	Repository_Commits = []

	data2 = svn_data.split(" | ")
	for m in xrange(1 , len(data2), 3):
		date = data2[m+1][0:10]
		month = date[0:7]
		year = date[0:4]
		contributer = data2[m]
		revision = data2[m-1].replace("-", "").split()[-1]
		revision = revision[1:]
		ticket = ""
		regex = re.compile(ur'\[[-+~]\]\s([A-Z]*-[0-9]*)', re.MULTILINE)
		group = re.findall(regex, data2[m-1])
		if group is not None and len(group) > 0:
			ticket = group[0]
		
		# if revision == _rev:
			# continue
		if revision > _rev or _rev == "":
			Repository_Commits.append((date, contributer, revision, ticket))

	return Repository_Commits


def selectRepository_Commits():
	# print """SELECT * from Repository_Commits WHERE Repository_ID = {0}
		 # ORDER BY Repository_Revision DESC LIMIT 1""".format(_repo_id)

	print """SELECT a.Repository_ID, 
					a.Repository_Name, 
					b.Repository_Revision 
			FROM Repository AS a LEFT JOIN Repository_Commits AS b ON 
					a.Repository_ID = b.Repository_ID 
			WHERE 
					b.Repository_Revision = (SELECT Repository_Revision FROM Repository_Commits 
											WHERE Repository_ID = a.Repository_ID 
											ORDER BY Repository_Revision DESC LIMIT 1);"""




def insertRepository_Commits(commits):
	# if Repository_ID > 0 then 
	# if Repository_Revision <> Rev
	# insert to mysql
	for commit in commits:
		_contributer = commit[1]
		_commit_date = commit[0]
		_revision = commit[2]
		print """INSERT INTO Repository_Commits SET 
			Repository_ID='{0}', 
			Repository_Contributer='{1}',
			Repository_Commit_Date='{2}',
		Repository_Revision='{3}'
		""".format(repo_id, _contributer, _commit_date, _revision)




def selectJiraDashboard():
	global cur
	sql = """
		SELECT Jira_Issue_Stats_ID, Jira_Dashboard_ID FROM Jira_Issue_Stats;
	"""	
	cur.execute(sql)	
	index = dict( (d[0], i) for i, d in enumerate(cur.description) )
	rows = cur.fetchall()
	dashboards = []
	for row in rows:
		dashboards.append( (row[index['Jira_Issue_Stats_ID']], row[index['Jira_Dashboard_ID']]) )
	return dashboards

def formatDate(_string):
	return str(datetime.datetime.strptime(_string.split(" ")[0], '%d/%b/%y'))


def updateJiraDashboard(_id, _packet):

	sql = """
		UPDATE Jira_Issue_Stats 
		SET 
			Jira_Issues_In_Progress='{0}',
			Jira_Issues_Closed='{1}',
			Jira_Issues_Total='{2}',
			Jira_Sprint_startDate='{3}',
			Jira_Sprint_endDate='{4}',
			Jira_Sprint_Name='{5}'
		WHERE
			Jira_Issue_Stats_ID='{6}'

	""".format(_packet[0], _packet[1], _packet[2], formatDate(_packet[3]), formatDate(_packet[4]), _packet[5], _id)
	# print sql
	global cur, conn
	cur.execute(sql)
	conn.commit()


def updateJiraIssues(_dashboard, _issues):
	# print _issues
	sql = """
		DELETE FROM Jira_Issues WHERE Jira_Dashboard_ID = '{0}'
	""".format(_dashboard)

	global conn, cur

	# print sql
	cur.execute(sql)
	conn.commit()

	if isinstance(_issues, collections.Iterable):
		for issue in _issues:
			
			sql = """
				INSERT 
					INTO Jira_Issues 
				SET 
					Jira_Dashboard_ID='{0}',
					Jira_Summary='{1}',
					Jira_Key = '{2}',
					Jira_Label = '{3}'

			""".format(_dashboard, issue.Summary, issue.JiraKey, ",".join(issue.Labels) )
			

			cur.execute(sql)
			conn.commit()


def GetTEST(_server, _resource, _name):
	global SONAR_URL, SONAR_USER, SONAR_PASSWORD
	url = "http://" + _server + SONAR_URL + _resource + "&metrics=" + _name
	# print url
	data = getJson(url, [SONAR_USER, SONAR_PASSWORD])
	# print data
	if data is not None:
		if len(data) > 0:
			data = data[0]
			if data is not None and "msr" in data and len(data['msr']) > 0:
				return data['msr'][0]['frmt_val']




def selectSonarTests():
	sql = """
		SELECT a.Sonar_Project_Lookup_ID, d.Sonar_Test_Type, b.Sonar_Server, c.Sonar_Resource_Name FROM Sonar_Project_Lookup AS a LEFT JOIN
					Sonar AS b ON a.Sonar_ID=b.Sonar_ID LEFT JOIN
					Sonar_Resource AS c ON a.Sonar_Resource_ID = c.Sonar_Resource_ID LEFT JOIN
					Sonar_Test_Types AS d ON a.Sonar_Test_Type_ID = d.Sonar_Test_Type_ID

	"""

	global conn, cur
	cur.execute(sql)
	index = dict( (d[0], i) for i, d in enumerate(cur.description) )
	rows = cur.fetchall()
	sonarTests = []
	for row in rows:
		# print row
		sonarTests.append( (row[index['Sonar_Project_Lookup_ID']], 
							row[index['Sonar_Server']], 
							row[index['Sonar_Resource_Name']], 
							row[index['Sonar_Test_Type']]) )
	return sonarTests

def insertSonarTests(_lookup, _result):
	sql = """
		INSERT INTO Sonar_Test_Results SET
			Sonar_Project_Lookup_ID='{0}',
			Sonar_Results='{1}',
			Sonar_Test_Results_Created=NOW();
	""".format(_lookup, _result);
	global cur, conn
	cur.execute(sql)
	conn.commit()

def selectCommits():
	sql = """
		SELECT  a.Repository_ID,
				a.Repository_Name, 
				a.Repository_Link, 
				MAX(b.Repository_Revision) AS Repository_Revision 
		FROM Repository AS a LEFT JOIN 
			 Repository_Commits AS b 
		ON a.Repository_Id = b.Repository_ID 
		GROUP BY Repository_ID;
	"""
	global cur, conn
	cur.execute(sql)
	rows = cur.fetchall()
	index = dict( (d[0], i) for i, d in enumerate(cur.description) )

	commits = []
	for row in rows:
		commits.append( (row[index['Repository_ID']], row[index['Repository_Link']], row[index['Repository_Revision']] or "") )
	return commits

def deleteCommits():
	sql = """
		DELETE FROM Repository_Commits;
	"""

	global cur,conn
	cur.execute(sql)
	conn.commit()



def insertCommits(_id, _packet):
	sql = """
		INSERT INTO Repository_Commits SET 
					Repository_ID='{0}',
					Repository_Revision='{1}',
					Repository_Contributer='{2}',
					Repository_Commit_Date='{3}',
					Repository_Ticket='{4}'
	""".format(_id, _packet[0], _packet[1], _packet[2], _packet[3])

	global cur,conn
	cur.execute(sql)
	conn.commit()


def checkJobStat(_stats, _job, _build):
	if (_stats is None or len(_stats) == 0):
		print _job
		return True

	else:
		# print _job
		ids = [ i[0] for i in _stats ]
		# print ids

		for stat in _stats:
			# print _job
			# print stat
			# print _build
			# print "======"

			print _job
			print _build
			if stat[0] == _job[1]:
				# if _build[0] > stat[1]:
				if _build.BuildId > stat[1]:
					return True
			else:
				if _job[1] not in ids:
					return True

			# if int(_build[0]) > int(stat[1]) :
			# 	print str(stat[1])
			# 	# print ","
			# 	# print stat[0]
			# 	print ","
			# 	print str(_build[0])
			# 	# print ","
			# 	# print str(job[1]) + "\n"
			# if ( (int(stat[0]) == int(_job[1]) and int(_build[0]) > int(stat[1]) ) or (int(stat[0]) != int(job[1]) and int(job[1] not in ids))  ):
			# 	print stat[0]
			# 	print ","
			# 	print job[1]
			# 	return True
			# else:
				# return False
	return False


def selectArtifactory():
	sql = """
		SELECT 
			c.Artifactory_ID, 
			c.Artifactory_Name 
		FROM 
			CQM_Projects AS a 
		LEFT JOIN 
			Artifactory_Project_Lookup AS b ON a.Project_ID = b.Project_ID 
		LEFT JOIN 
			Artifactory AS c ON c.Artifactory_ID = b.Artifactory_ID
		WHERE c.Artifactory_Name is not NULL;

	"""

	global cur, conn
	cur.execute(sql)
	rows = cur.fetchall()

	return rows
	

def sortArtifactory(element):
	return element['uri']

def sortFiles(el):
	return el[0]

# def getListFiles( _artifactory, _iffile = False):
# # curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
# 	global ARTIUSER, ARTIPASS, artifactory_server
# 	command_curl_get_list = "curl -X GET -u " + ARTIUSER + ":" + ARTIPASS + " " + _artifactory
# 	print command_curl_get_list
# 	curl_get_list = sb.Popen(shlex.split(str(command_curl_get_list)), stdout=sb.PIPE)
# 	data_curl_get_list = curl_get_list.communicate()[0]

# 	if _iffile == True:
# 		print data_curl_get_list
# 		return data_curl_get_list

# 	p = re.compile(ur'({.*})', re.DOTALL)
# 	group = re.search(p, data_curl_get_list)

# 	if group is not None:
# 		files = []

# 		data_json = json.loads(group.groups()[0])
# 		if "children" in data_json:
# 		  return data_json['children']
# 		else:
# 		  msg = "[ERROR] Artifactory " + _folder + " is empty or service not found"
# 		  print msg





## update Sprints Details
def updateSprintsDetails():
	dashboards = selectJiraDashboard()
	print dashboards
	for dashboard in dashboards:
		latestSprint, lastestSprintName = getJiraLatestSprint(dashboard[1])
		print "latestSprint"
		print latestSprint
		print lastestSprintName


		data = getJiraSprintDetails(dashboard[1], latestSprint)
		
		if data is not None and len(data) >= 5:
			print data[5]
			packet = []
			packet.append(data[0])
			packet.append(data[1])
			packet.append(data[2])
			packet.append(data[3])
			packet.append(data[4])
			packet.append(lastestSprintName)
			updateJiraDashboard(dashboard[0], packet)
			

			updateJiraIssues(dashboard[1], data[5])


## update Sonar Tests Details
def updateSonarTestsDetails():
	sonarTests = selectSonarTests()
	# print sonarTests
	for test in sonarTests:
		if test is not None and test[0] is not None and test[1] is not None and test[2] is not None and test[3] is not None:
			sonarResult = GetTEST(test[1], test[2], test[3])
			if test[0] is not None and sonarResult is not None:
				insertSonarTests(test[0], sonarResult)

def updateSVNCommitsDetails():
	deleteCommits()
	svnCommits = selectCommits()
	# print svnCommits
	for commit in svnCommits:
		dataCommit = getLogSvn(commit[1], commit[2]) or "Error"
		# print dataCommit
		if type(dataCommit) is not str:
			for entry in dataCommit:
				# print i[2] + commit[2]
				if (commit[2] is not None  and entry[2] != commit[2]) or commit[2] is not None:
					# print entry
					insertCommits(commit[0], ( entry[2], entry[1], entry[0], entry[3] ))
					# print entry[0]
					# print (( entry[2], entry[1], entry[0] ))


def updateJenkinsDetails():
	jenkinsJobs = selectJenkinsJobs()
	jenkinsJobStats = selectJenkinsJobStats()

	print "jenkinsJobs"
	# print jenkinsJobs
	# print jenkinsJobStats


	for job in jenkinsJobs:
		# print job
		if jenkinsRunningJobs(job[2]) == True:
			continue
		jenkinsBuilds = getJenkinsBuilds(job[0], job[2])
		# print job[1]
		# print jenkinsBuilds
		for build in jenkinsBuilds:
			# print "job: "
			# print job
			# print "build"
			# print build
			if checkJobStat(jenkinsJobStats, job, build):
				# insertJenkinsJobStats(job[1], (build[0],build[3],build[1],build[2], build[4], build[5], build[6], build[7]))
				insertJenkinsJobStats(job[1], build)
			# if jenkinsJobStats is not None and len(jenkinsJobStats) > 0:
				# for stat in jenkinsJobStats:
				# 	print str(stat[0]) + "=" + str(job[1]) + " , " + str(build[0]) + "!=" + str(stat[1])
				# 	if ( (int(stat[0]) == int(job[1]) and int(build[0]) > int(stat[1]) ) or (int(stat[0]) != int(job[1])) ):
				# 		insertJenkinsJobStats(job[1], (build[0],build[3],build[1],build[2]))



	# for job in jenkinsJobs:
	# 	insertJenkinsJobStats(job[0], (build[0],build[3],build[1],build[2]))


updateSprintsDetails()
updateSonarTestsDetails()
updateSVNCommitsDetails()
updateJenkinsDetails()

artifactories = selectArtifactory()
print "artifactories" + str(artifactories)
files = []
for artifactory in artifactories:
	list = getListFiles(str(artifactory[1]))
	if list is not None:
		for item in list:
			_file = str(artifactory[1]) + item['uri']
			# print _file
			json_tmp = getListFiles(str(_file), None, True)
			# print json_tmp
			_file_json = json.loads(json.dumps(json_tmp))
			
			if "created" in _file_json and "downloadUri" in _file_json:
				files.append( (_file_json['created'][:19], _file_json['downloadUri']) )
	
files.sort( key=sortFiles )
print files[-5:]


sql = """ 
			DELETE FROM Artifactory_Bundles;
		"""

# print sql
# global cur, conn
cur.execute(sql)
conn.commit()


for artifactory in artifactories:
	items = getLastPromote(artifactory[1])
	if items is not None:
		for item in items:

			Artifactory_Bundles_Name = item[0].split("/")[1]
			print "Date to convert: " + item[1][:19]
			Artifactory_Bundles_Date = datetime.datetime.strptime(item[1][:19], "%Y-%m-%dT%H:%M:%S")
			Artifactory_ID = artifactory[0]
			sql = """ 
				INSERT INTO Artifactory_Bundles SET Artifactory_Bundles_Name='{0}', Artifactory_Bundles_Date = '{1}', Artifactory_ID = '{2}';
			""".format(Artifactory_Bundles_Name, Artifactory_Bundles_Date, Artifactory_ID)

			# print sql
			# global cur, conn
			cur.execute(sql)
			conn.commit()


def toInt(variable):
	try:
		return int(variable)
	except ValueError:
		return 0
	except TypeError:
		return 0

def getVersionsFromDB(Project_ID):
	sql = "SELECT * FROM jira_version WHERE ProjectId != 10 AND ProjectId = {0}".format(Project_ID)
	global conn, cur
	cur.execute(sql)
	rows = cur.fetchall()
	index = dict( (d[0], i) for i, d in enumerate(cur.description) )
	dbVersions = []
	for row in rows:
		version = Version()
		version.Id = row[index['VersionId']]
		version.VersionId = row[index['VerId']]
		version.StatusId = row[index['StatusId']]

		dbVersions.append(version)
	return dbVersions


def getVersionIssuesFromDB(versionId):
	sql = "SELECT * FROM jira_version_issues WHERE VersionId = '{0}'".format(versionId)
	print sql
	global conn, cur
	cur.execute(sql)
	rows = cur.fetchall()
	index = dict( (d[0], i) for i, d in enumerate(cur.description) )
	dbVersionIssues = []

	for row in rows:
		dbVersionIssues.append( (row[index['StatusId']],
								row[index['JiraKey']],
								row[index['VersionId']],
								row[index['VersionIssueId']]))


	return dbVersionIssues


def getProjectsVersion():
	sql = """SELECT * FROM CQM_Projects WHERE Project_ID != 10 AND Project_Version is not NULL"""
	cur.execute(sql)
	# conn.commit()
	rows = cur.fetchall()
	return rows



def updateJiraVersions(_projectId, _projectName):
	Project_ID = _projectId
	dbVersions = getVersionsFromDB(Project_ID)
	# print dbVersions

	projectName = _projectName

	versionsInProject = getJson("http://10.33.20.21:8080/jira/rest/api/latest/project/{0}/versions".format(projectName) , ["cqm_test1", "cqmtest"])

	newVersions = []

	if versionsInProject is not None:
		for version in versionsInProject:
			
		## this order  matters
			version['status'] = 0

			if version['archived'] == True:
				version['status'] = 2

			if version['released'] == True:
				version['status'] = 1

			if "releaseDate" not in version:
				version['releaseDate'] = ""


			newVersion = Version()
			newVersion.StatusId = version['status']
			newVersion.VersionId = version['id']
			newVersion.ReleaseDate = version['releaseDate']
			newVersion.VersionName = version['name']

			# newVersions.append((version['name'], version['status'], version['id'], version['releaseDate']))
			newVersions.append(newVersion)


	# print newVersions

	for version in newVersions:
		# versionName = version[0]
		versionName = version.VersionName
		# versionId = version[2]
		versionId = version.VersionId
		issuesInVersion = getJson("http://10.33.20.21:8080/jira/rest/api/2/search?jql=fixVersion={0}".format(versionId) , ["cqm_test1", "cqmtest"])

		oldVersion = None

		for item in dbVersions:
			# if int(item[1]) == int(version[2]):
			if int(item.VersionId ) == int(version.VersionId):
				oldVersion = item

		

	### brand new version	
		if oldVersion is None:
	
			sql = """INSERT INTO jira_version SET 
						VerName='{0}', 
						ProjectId='{1}', 
						StatusId='{2}',
						VerId='{3}',
						ReleaseDate='{4}'
					""".format(version.VersionName, Project_ID, version.StatusId, version.Id, version.ReleaseDate)
			print sql

			cur.execute(sql)
			conn.commit()

			insertedVersionId = cur.lastrowid

			print sql
			if "issues" in issuesInVersion:
				for issue in issuesInVersion['issues']:
					# print issues['key'] + " " + issues['fields']['summary'] + " - " + issues['fields']['status']['name']


					issueKey = issue['key']
					issueSummary = issue['fields']['summary']

					issueStatus = 3
					tmpStatus = issue['fields']['status']['name']

					if issue['fields']['issuetype']['id'] == "5":
						continue


					if tmpStatus == "Closed":
						issueStatus = 4
					if tmpStatus in ["In Dev", "In Progress", "In Development"]:
						issueStatus = 5
					if tmpStatus == "Open":
						issueStatus = 3


					issueEstimatedTime = "0"
					if "timeestimate" in issue['fields']:
						issueEstimatedTime = toInt(issue['fields']['timeestimate'])


					issueTimeSpent = "0"
					if "timespent" in issue['fields']:
						issueTimeSpent = toInt(issue['fields']['timespent'])


					
					issueProgress = "0"
					if "progress" in issue['fields']['aggregateprogress']:
						issueProgress = toInt(issue['fields']['aggregateprogress']['progress'])




					issueTotal = "0"
					if "total" in issue['fields']['aggregateprogress']:
						issueTotal = toInt(issue['fields']['aggregateprogress']['total'])

					issuePercent = "0"
					if "percent" in issue['fields']['aggregateprogress']:
						issuePercent = toInt(issue['fields']['aggregateprogress']['percent'])

					issueLabel = str(",".join(issue['fields']['labels']))


					# if version released, archive or issue closed,deleted
					# if version[1] > 0 or issueStatus == 4 or issueStatus == 6:
					if version.StatusId > 0 or issueStatus in [4, 6]:
						issueProgress = 100
						issuePercent = 100

					sql = """INSERT INTO jira_version_issues SET
								VersionId ='{0}',
								JiraKey='{1}',
								StatusId='{2}',
								summary='{3}',
								EstimatedTime='{4}', 
								TimeSpent='{5}',
								Progress='{6}',
								Total='{7}',
								Percent='{8}',
								label='{9}'
					""".format(insertedVersionId, issueKey, issueStatus, issueSummary.replace("'", "&#39;").encode("utf-8"), issueEstimatedTime, issueTimeSpent, issueProgress, issueTotal, issuePercent, issueLabel)
					print sql
					cur.execute(sql)
					conn.commit()



	###version changed status or open version

		# if oldVersion is not None and (int(oldVersion[2]) != int(version[1]) or version[1] == 0):
		if oldVersion is not None and (int(oldVersion.VersionId) != int(version.VersionId) or version.VersionId == 0):


			sql = """UPDATE jira_version SET 
						StatusId = '{0}',
						ReleaseDate='{2}'
					WHERE VersionId = '{1}'
			""".format(version.StatusId, oldVersion.Id, version.ReleaseDate )

			print sql
			cur.execute(sql)
			conn.commit()

			insertedVersionId = oldVersion[0]

			# dbVersionIssues = getVersionIssuesFromDB(oldVersion[0])
			dbVersionIssues = getVersionIssuesFromDB(oldVersion.Id)
			# print dbVersionIssues

			if "issues" in issuesInVersion:

				for issue in issuesInVersion['issues']:


					issueKey = issue['key']
					issueSummary = issue['fields']['summary']

					issueStatus = 3
					tmpStatus = issue['fields']['status']['name']
					if tmpStatus == "Closed":
						issueStatus = 4
					if tmpStatus in ["In Dev", "In Progress", "In Development"]:
						issueStatus = 5
					if tmpStatus == "Open":
						issueStatus = 3


					issueEstimatedTime = "0"
					if "timeestimate" in issue['fields']:
						issueEstimatedTime = toInt(issue['fields']['timeestimate'])


					issueTimeSpent = "0"
					if "timespent" in issue['fields']:
						issueTimeSpent = toInt(issue['fields']['timespent'])


					
					issueProgress = "0"
					if "progress" in issue['fields']['aggregateprogress']:
						issueProgress = toInt(issue['fields']['aggregateprogress']['progress'])


					issueTotal = "0"
					if "total" in issue['fields']['aggregateprogress']:
						issueTotal = toInt(issue['fields']['aggregateprogress']['total'])

					issuePercent = "0"
					if "percent" in issue['fields']['aggregateprogress']:
						issuePercent = toInt(issue['fields']['aggregateprogress']['percent'])



					oldIssue = None
					for item in dbVersionIssues:
						if item[1] == issue['key']:
							oldIssue = item

					if oldIssue is not None:
						# update existing issue
						# print oldIssue

						newStatus = 3
						tmp = str(issue['fields']['status']['name'])
						# print tmp
						if tmp == "Closed":
							newStatus = 4
						if tmp == "In Progress" or tmp == "In Dev":
							newStatus = 5

						if int(oldIssue[0]) != int(newStatus):
							# print  str(oldIssue[0]) + "!=" + str(newStatus)
							sql = """UPDATE jira_version_issues SET 
										StatusId = '{0}',
										EstimatedTime='{2}', 
										TimeSpent='{3}',
										Progress='{4}',
										Total='{5}',
										Percent='{6}' 
									WHERE VersionIssueId = '{1}'
							""".format(newStatus, oldIssue[3], issueEstimatedTime, issueTimeSpent, issueProgress, issueTotal, issuePercent)
							print sql
							cur.execute(sql)
							conn.commit()
					else: 
						# new issue
						sql = """INSERT INTO jira_version_issues SET
								VersionId ='{0}',
								JiraKey='{1}',
								StatusId='{2}',
								summary='{3}',
								EstimatedTime='{4}', 
								TimeSpent='{5}',
								Progress='{6}',
								Total='{7}',
								Percent='{8}'
						""".format(insertedVersionId, issueKey, issueStatus, issueSummary.encode("utf-8").replace("'", "&#39;"), issueEstimatedTime, issueTimeSpent, issueProgress, issueTotal, issuePercent)
						print sql
						cur.execute(sql)
						conn.commit()

				# find deleted, set progress 100%, set flag as deleted
				for issue in dbVersionIssues:

					deletedIssue = True

					for item in issuesInVersion['issues']:
						if issue[1] == item['key']:
							deletedIssue = False

					if deletedIssue == True:
						sql = """UPDATE jira_version_issues SET 
										StatusId = '{0}',
										Percent='{1}' 
									WHERE VersionIssueId = '{2}'
							""".format(6, 100, issue[3])
						print sql
						cur.execute(sql)
						conn.commit()


		

					

				
projects = getProjectsVersion()

for project in projects:
	projectName = project[3]
	projectId = project[0]
	updateJiraVersions(projectId, projectName)
	print "project=" + str(project)



print "finished"

