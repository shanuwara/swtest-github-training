#!python2.7 -u

import shlex
import sys
import os
import json
import urllib2
import base64
import subprocess as sb
import re
import hashlib
import json




global JIRAUSER, JIRAPASSWD, JIRAKEY, ENVIRONMENT, VALIDATION_ONLY, HOT_RELEASE, BUILD_NUMBER, BUILD_ID, EAR_FILES, NUMBER_OF_EAR, NUMBER_OF_ARTIFACT, NUMBER_OF_CONFIG, Destination_dir, SUFFIX
global FOLDER, REPORTER
Destination_dir = "/opt/tibco/cqm_eis_deployment"
# JIRAUSER="CQMJIRA"
global mail
mail = open("Mail.txt", "w")


global SVN_SCRIPTS
SVN_SCRIPTS = "http://10.33.20.5:8080/svn/eis/trunk/Development/Build/"
SVN_BW = "http://10.32.18.100/svn/eis/trunk/Development/Code/Bw/"


def setEnv(_variable, notrequired = False):
  if _variable in os.environ and os.environ[_variable].split() != "":
    # globals()[_variable]
    globals()[_variable] = os.environ[_variable]
  else:
    if notrequired == False:
      msg = "[ERROR] " + _variable + " is not set"
      print msg
      mail.write(msg)
      sys.exit(-1)

setEnv('JIRAPASSWD')
# setEnv('JIRAKEY')
setEnv('JIRAUSER')
setEnv('ENVIRONMENT')
setEnv('HOT_RELEASE')
setEnv('BUILD_NUMBER')
setEnv('BUILD_ID')
# setEnv('EAR_FILES')
setEnv('SERVICE')
setEnv('SVNUSER')
setEnv('SVNPASS')
setEnv('WORKSPACE')
setEnv('VALIDATION_ONLY')
setEnv('ARTIUSER')
setEnv('ARTIPASS')
setEnv('ARTISOURCE')
setEnv('FOLDER')
setEnv('JIRAKEY', True)
setEnv('REPORTER', True)



if "REPORTER" in globals() and REPORTER is not None and REPORTER != "":
  REPORTER = REPORTER.split(":")[0]
  msg = "[INFO] Triggered by " + REPORTER + "\n"
  mail.write(msg)
  mail.flush()
  print msg



if VALIDATION_ONLY == "YES":
  setEnv('RC')
else:
  setEnv('RC', True)

setEnv('REGRESSION_TEST', True)
setEnv('EMS_SCRIPTS', True)
setEnv('COUCHBASE_SCRIPTS', True)


if VALIDATION_ONLY == "NO" and ARTISOURCE =="trunk":
  msg = "[ERROR] Cannot deploy from trunk, please promote before"
  print msg
  mail.write(msg)
  sys.exit(-1)

# print os.environ

# first validate in PROD
if ENVIRONMENT.find("PROD") != -1:
  VALIDATION_ONLY = "YES"
  RC = "LIVE"



os.chdir(WORKSPACE)
properties = file("properties.cfg", "w")


global repository, artifactory_server
repository = "EIS_DEVOPS"
artifactory_server = "http://10.33.20.7:8080/artifactory/api/storage/" + repository + "/"


def getCategories():

  cmd = """
    curl --user '{0}':'{1}' -X GET http://10.32.18.100/svn/eis/cqm/AutoDeployment/EIS_Service_Category_Mapping.txt
    """.format(SVNUSER,SVNPASS)
  sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
  data_cmd = sb_cmd.communicate()[0]

  data = data_cmd.split("\n")
  for item in data:
    if item.find(SERVICE) != -1:
      sub_item = item.split("|")
      return sub_item[1]

  return "all"


def getListFiles( _folder, _exception = True):
# curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
  global ARTIUSER, ARTIPASS, artifactory_server
  command_curl_get_list = "curl -D- -X GET -u " + ARTIUSER + ":" + ARTIPASS + " " + artifactory_server + _folder + "/" 
  print command_curl_get_list
  curl_get_list = sb.Popen(shlex.split(command_curl_get_list), stdout=sb.PIPE)
  data_curl_get_list = curl_get_list.communicate()[0]
  # print data_curl_get_list
  # data_curl_get_list = curl_get_list.stdout.read()
  p = re.compile(ur'({.*})', re.DOTALL)
  group = re.search(p, data_curl_get_list)
  # print group.groups()
  if group is not None:
    files = []
    # print group.groups()[0]
    data_json = json.loads(group.groups()[0])
    if "children" in data_json:
      return data_json['children']
    else:
      msg = "[ERROR] Artifactory " + _folder + " is empty or service not found"
      print msg
      mail.write(msg)
      if _exception == False:
        msg = "[INFO] Folder " + _folder + " allowed to be empty\n"
        print msg
        mail.write(msg)
        mail.flush()
      else:
        sys.exit(-1)



def getAllPaths():
  command_svn_list = "svn --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" " + " list " + SVN_BW + " -R "
  print "[INFO] " + command_svn_list
  sb1 = sb.Popen(shlex.split(command_svn_list), stdout=sb.PIPE)
  data_in = sb1.stdout.read()
  sb2 = sb.Popen(shlex.split("egrep \"/$\""), stdout=sb.PIPE, stdin=sb.PIPE)
  data_out = sb2.communicate(input=data_in)[0]
  return data_out


def getServicePath(_service, _data_svn_list):


  # data_svn_list = data_out
  data_svn_list = _data_svn_list

  data_svn_list = data_svn_list.split("\n")
  # print "[INFO] " + str(data_svn_list)

  for p in range(0, len(data_svn_list)):
    tmp = data_svn_list[p].split("/")
    # print tmp
    if  len(tmp) > 1 and tmp[-2] == _service:

      REPOSITORY_EXEC = ""
      REPOSITORY_EXEC = "/".join(tmp)
      REPOSITORY_EXEC = os.path.join(SVN_BW, REPOSITORY_EXEC)
      group = re.search(ur'http.*\/[0-9]\.[0-9]\/.*\/$', REPOSITORY_EXEC)
      if group != None and len(group.group()) > 0:
        print "[INFO] " + str(group.group())
        print "[INFO] " + str(REPOSITORY_EXEC)
        return REPOSITORY_EXEC



def getLatestFile(_list, _service):
  files = []
  for f in _list:
    group = re.search(ur'^('+ _service + ').*zip$', str(f['uri'][1:]))
    if group is not None and len(group.groups()) > 0 and group.groups()[0] == SERVICE:
      # print group.groups()
      files.append(str(f['uri'][1:]))

  # files = sorted(files)
  # files.sort(key=str.lower)
  files.sort(key=lambda x:int(x.split("_")[2]))
  # print files[-1][1:]
  if len(files) > 0:
    return files[-1]
  else:
    return None



def uploadToFolder(_file, _folder):
# curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
  global ARTIUSER, ARTIPASS, repository
  artifactory_server = "http://10.33.20.7:8080/artifactory/simple/" + repository + "/"
  preHash = open(_file, "rb").read()
  hash_md5 = hashlib.md5(preHash).hexdigest()
  hash_sha1 = hashlib.sha1(preHash).hexdigest()
  command_curl_upload = "curl -D- -X PUT -u " + ARTIUSER + ":" + ARTIPASS + " " + artifactory_server + _folder + "/ -T " + _file + " -H 'X-Checksum-Md5: " + hash_md5 + "' -H 'X-Checksum-Sha1: " + hash_sha1 + "'"
  print command_curl_upload
  curl_upload = sb.Popen(shlex.split(command_curl_upload), stdout=sb.PIPE)
  data_curl_upload = curl_upload.stdout.read()

  # print data_curl_upload
  if data_curl_upload.find("201 Created") == -1:
    msg = "[ERROR] File has not been uploaded to artifactory properly: " + data_curl_upload
    print msg
    mail.write(msg)
    sys.exit(-1)
  else:
    msg = "[INFO] " + data_curl_upload
    print msg
    mail.write(msg)


def promoteToSIT(_file, _folder):
  if _file is None:
    msg = "[ERROR] Artifactory trunk is empty or service not found (" + SERVICE + ")"
    mail.write(msg)
    print msg
    sys.exit(-1)

 


  global ARTIUSER, ARTIPASS, repository
  artifactory_server = "http://10.33.20.7:8080/artifactory/" + repository + "/"
  print "ARTIUSER" + str( ARTIUSER)
  print "ARTIPASS" + str( ARTIPASS)
  print "artifactory_server" + str( artifactory_server)
  print "_file" + str( _file)
  command_curl_download = "curl -X GET -u " + ARTIUSER + ":" + ARTIPASS + " " + artifactory_server + ARTISOURCE + "/" + _file + " -o " + _file
  print command_curl_download
  curl_download = sb.Popen(shlex.split(command_curl_download), stdout=sb.PIPE)
  data_curl_download = curl_download.communicate()[0]
  print data_curl_download
  print ENVIRONMENT
  print SUFFIX


  cmd = "zipinfo -1 " + _file
  print cmd
  os.system("ls -lah")
  sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
  data = sb_cmd.communicate()[0]

  configFound = False
  if data is not None:
    for config in data.split("\n"):
      if config.find(SUFFIX) != -1:
        configFound = True
        break

  if configFound == False:
    msg = "[ERROR] Config file not found for " + SUFFIX + "\n"
    mail.write(msg)
    mail.flush()
    print msg
    sys.exit(-1)


  if "EMS_SCRIPTS" in os.environ and EMS_SCRIPTS is not None and EMS_SCRIPTS != "" and VALIDATION_ONLY == "NO":
    os.chdir(WORKSPACE)
    # os.system("rm -rf " + WORKSPACE + "/" + EMS_SCRIPTS)
    os.system("rm -rf " + WORKSPACE + "/ems")
    os.mkdir(WORKSPACE + "/ems")
    # command_list_script_ems = "svn co --username=" + SVNUSER + " --password=" + SVNPASS + " "  + SVN_SCRIPTS + EMS_SCRIPTS + "/" + SUFFIX + " " + EMS_SCRIPTS + " --force --non-interactive"
    command_list_script_ems = "svn co --username=" + SVNUSER + " --password=" + SVNPASS + " "  + SVN_SCRIPTS + "Ems/" + EMS_SCRIPTS + " ems/" + EMS_SCRIPTS +" --force --non-interactive"
    print command_list_script_ems
    list_script_ems = sb.Popen(shlex.split(command_list_script_ems), stdout=sb.PIPE)
    data_list_script_ems = list_script_ems.communicate()[0]
    print data_list_script_ems

    print "rm -rf " + WORKSPACE + "/ems/" + EMS_SCRIPTS + "/.svn"
    os.system("rm -rf " + WORKSPACE + "/ems/" + EMS_SCRIPTS + "/.svn")

    # print "tar -cvf Ems.tar " + EMS_SCRIPTS
    # os.system("tar -cvf Ems.tar " + EMS_SCRIPTS)

    print "tar -cvf Ems.tar --directory=ems " + EMS_SCRIPTS
    os.system("tar -cvf Ems.tar --directory=ems " + EMS_SCRIPTS)

    print "zip -g " + _file + " Ems.tar"
    os.system("zip -g " + _file + " Ems.tar")


  if "COUCHBASE_SCRIPTS" in os.environ and COUCHBASE_SCRIPTS is not None and COUCHBASE_SCRIPTS != "" and VALIDATION_ONLY == "NO":
    os.chdir(WORKSPACE)
    # os.system("rm -rf " + WORKSPACE + "/" + COUCHBASE_SCRIPTS)
    os.system("rm -rf " + WORKSPACE + "/couchbase")
    os.mkdir(WORKSPACE + "/couchbase")
    # command_list_script_couchbase = "svn co --username=" + SVNUSER + " --password=" + SVNPASS + " "  + SVN_SCRIPTS + COUCHBASE_SCRIPTS + "/" + SUFFIX + " " + COUCHBASE_SCRIPTS + " --force --non-interactive"
    command_list_script_couchbase = "svn co --username=" + SVNUSER + " --password=" + SVNPASS + " "  + SVN_SCRIPTS + "Couchbase/" + COUCHBASE_SCRIPTS + " couchbase/" + COUCHBASE_SCRIPTS + " --force --non-interactive"
    print command_list_script_couchbase
    list_script_couchbase = sb.Popen(shlex.split(command_list_script_couchbase), stdout=sb.PIPE)
    data_list_script_couchbase = list_script_couchbase.communicate()[0]
    print data_list_script_couchbase

    print "rm -rf " + WORKSPACE + "/couchbase/" + COUCHBASE_SCRIPTS + "/.svn"
    os.system("rm -rf " + WORKSPACE + "/couchbase/" + COUCHBASE_SCRIPTS + "/.svn")

    # print "tar -cvf Couchbase.tar " + COUCHBASE_SCRIPTS
    # os.system("tar -cvf Couchbase.tar " + COUCHBASE_SCRIPTS)

    print "tar -cvf Couchbase.tar --directory=couchbase " + COUCHBASE_SCRIPTS
    os.system("tar -cvf Couchbase.tar --directory=couchbase " + COUCHBASE_SCRIPTS)


    print "zip -g " + _file + " Couchbase.tar"
    os.system("zip -g " + _file + " Couchbase.tar")


  os.system("cp " + _file + " " + _file + ".copy")

  # delete all config files except one related with environment
  pos = _file.find("_")
  if pos != -1:
    tmp = _file[0:pos]
    print tmp
    command_leave_config = "zip -d " + _file + " cfg/* -x cfg/" + tmp + "-" + SUFFIX + ".cfg"
    print command_leave_config
    leave_config = sb.Popen(shlex.split(command_leave_config), stdout=sb.PIPE)
    data_leave_config = leave_config.communicate()[0]
    print data_leave_config







def zipFile(_filein, _fileout):
  command_zip_file = "zip -r " + _fileout + " " + _filein
  zip_file = sb.Popen(shlex.split(command_zip_file), stdout=sb.PIPE)
  data_zip_file = zip_file.stdout.read()
  msg = "[INFO] " + data_zip_file
  print msg
  mail.write(msg)


def JiraGetData(JIRAKEY):
  url = os.path.join("http://10.33.20.21:8080/jira/rest/api/2/issue", JIRAKEY)
  print url
  req = urllib2.Request(url)
  # print "Authorization", "Basic " + base64.b64encode(JIRAUSER + ":" + JIRAPASSWD)
  req.add_header("Authorization", "Basic " + base64.b64encode(JIRAUSER + ":" + JIRAPASSWD))
  resp = urllib2.urlopen(req)
  data = resp.read()
  data = json.loads(data.replace("\\r\\n", '$'))

  # print json.loads(json.dumps(data['fields']['comment']['comments'][0]))['body'].split("$")[1:-1]

  REPOSITORY_LIST = ""
  # REPOSITORY_LIST_TMP = data['fields']['comment']['comments']['body'].split("$")[1:-1]
  REPOSITORY_LIST_TMP = json.loads(json.dumps(data['fields']))#['comment']['comments'][0]))#['body'].split("$")[1:-1]
  # print REPOSITORY_LIST_TMP
  return REPOSITORY_LIST_TMP
  
  # for i in range(0, len(REPOSITORY_LIST_TMP)):
  #   # print REPOSITORY_LIST_TMP[i]
  #   if (REPOSITORY_LIST_TMP[i].find(".ear") != -1):
  #     print REPOSITORY_LIST_TMP[i]
  #     print i
  #     REPOSITORY_LIST += str(REPOSITORY_LIST_TMP[i][:-4]) + ","
  # REPOSITORY_LIST = REPOSITORY_LIST[:-1]
  # print REPOSITORY_LIST
  # return REPOSITORY_LIST

global JIRAKEY



# echo "JIRAKEY=$JIRAKEY" >> properties.cfg
# echo "ENVIRONMENT=$ENVIRONMENT" >> properties.cfg

# properties.write("JIRAKEY=" + JIRAKEY)
properties.write("ENVIRONMENT=" + ENVIRONMENT + "\n")
properties.write("PARENT_SUBJECT=EIS_Deployment_Test - Build # " + BUILD_NUMBER + " - " + BUILD_ID +"\n")
properties.write("VALIDATION_ONLY="+ VALIDATION_ONLY+"\n")








def back_up(_IP_address):
  backup_dir="/opt/tibco/release_backup/" + BUILD_NUMBER + "/"
  command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"set -x; rm -rf " + backup_dir + "; mkdir -p " + backup_dir+ "; mkdir -p /opt/tibco/applications/devops/deploy/ems/; mkdir -p /opt/tibco/applications/devops/deploy/couchbase/; cp -r /opt/tibco/applications/devops/deploy/ear/ " + backup_dir + "; cp -r /opt/tibco/applications/devops/deploy/cfg/ " + backup_dir + "; cp -r /opt/tibco/applications/devops/deploy/ems/ " + backup_dir + "; cp -r /opt/tibco/applications/devops/deploy/couchbase/ " + backup_dir + "\""
  print command
  command_sb = sb.Popen(shlex.split(command), stdout=sb.PIPE)
  data_command = command_sb.communicate()[0]
  print data_command  


def copy_tibco_artifact(_Ear_Bundles, _IP_address, _Destination_dir, _ENVIRONMENT):
  command1 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"rm -rf " + _Destination_dir + "; mkdir -p " + _Destination_dir + "\""
  print command1
  command1_sb = sb.Popen(shlex.split(command1), stdout=sb.PIPE)
  data_command1 = command1_sb.communicate()[0]
  print data_command1

  command2 = "scp -i /home/jenkinsci/.ssh/tibco_id_rsa " + _Ear_Bundles + " tibco@" + _IP_address + ":" + _Destination_dir
  print command2
  command2_sb = sb.Popen(shlex.split(command2), stdout=sb.PIPE)
  data_command2 = command2_sb.communicate()[0]
  print data_command2

  # command3 = "ssh -i ~/.ssh/tibco_id_rsa tibco@$" + _IP_address + " -C \"cd " + _Destination_dir + "; unzip " + _Ear_Bundles + "; cd temp; cp *.ear  /opt/tibco/applications/devops/deploy/ear/; cp *.cfg  /opt/tibco/applications/devops/deploy/cfg/; \""
  command3 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + _Destination_dir + "; unzip " + _Ear_Bundles + "; cp *.ear  /opt/tibco/applications/devops/deploy/ear/; cp cfg/*.cfg  /opt/tibco/applications/devops/deploy/cfg/; \""
  print command3
  command3_sb = sb.Popen(shlex.split(command3), stdout=sb.PIPE)
  data_command3 = command3_sb.communicate()[0]
  print data_command3

  data_command4 = ""
  if "EMS_SCRIPTS" in os.environ and EMS_SCRIPTS is not None and EMS_SCRIPTS != "" and VALIDATION_ONLY == "NO":
    command4 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + _Destination_dir + "; tar xvf Ems.tar; mkdir -p /opt/tibco/applications/devops/deploy/ems/" + EMS_SCRIPTS + "/*;  rm -rf /opt/tibco/applications/devops/deploy/ems/" + EMS_SCRIPTS + "/*; cp -r " + EMS_SCRIPTS + " /opt/tibco/applications/devops/deploy/ems/; rm -rf " + EMS_SCRIPTS + "\""
    # ssh -i ~/.ssh/tibco_id_rsa tibco@$IP_address -C "cd $Destination_dir; tar xvf Ems.tar; mkdir -p /opt/tibco/applications/devops/deploy/ems/$EMS_SCRIPTS/*;  rm -rf /opt/tibco/applications/devops/deploy/ems/$EMS_SCRIPTS/*; cp -r $EMS_SCRIPTS /opt/tibco/applications/devops/deploy/ems/; rm -rf $EMS_SCRIPTS"
    print command4
    command4_sb = sb.Popen(shlex.split(command4), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command4 = command4_sb.communicate()[0]


  data_command5 = ""
  if "COUCHBASE_SCRIPTS" in os.environ and COUCHBASE_SCRIPTS is not None and COUCHBASE_SCRIPTS != "" and VALIDATION_ONLY == "NO":
    command5 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + Destination_dir + "; tar xvf Couchbase.tar;  mkdir -p /opt/tibco/applications/devops/deploy/couchbase/" + COUCHBASE_SCRIPTS + "/*;  rm -rf /opt/tibco/applications/devops/deploy/couchbase/" + COUCHBASE_SCRIPTS + "/*; cp -r " + COUCHBASE_SCRIPTS + " /opt/tibco/applications/devops/deploy/couchbase/; rm -rf " + EMS_SCRIPTS + "\""
    print command5
    command5_sb = sb.Popen(shlex.split(command5), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command5 = command5_sb.communicate()[0]


  return data_command1 + "\n" + data_command2 + "\n" + data_command3 + "\n" + data_command4 + "\n" + data_command5 + "\n"




def deploy_couchbasescripts(_IP_ADDRESS):
  global VALIDATION_ONLY
  if VALIDATION_ONLY == "NO":
    if "COUCHBASE_SCRIPTS" in os.environ and COUCHBASE_SCRIPTS is not None and COUCHBASE_SCRIPTS != "":
      command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deployCouchbase.sh " + COUCHBASE_SCRIPTS + ";\" "
      print command
      command_sb = sb.Popen(shlex.split(command), stdout=sb.PIPE)
      data_command = command_sb.communicate()[0]
      print data_command
      






def deploy_emsscripts(_IP_ADDRESS):
  if VALIDATION_ONLY == "NO":
    if "EMS_SCRIPTS" in os.environ and EMS_SCRIPTS is not None and EMS_SCRIPTS != "":
      command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deployEms.sh " + EMS_SCRIPTS + ";\" "
      print command
      command_sb = sb.Popen(shlex.split(command), stdout=sb.PIPE)
      data_command = command_sb.communicate()[0]
      print data_command






def deploy_module(_EAR_NAME, _IP_ADDRESS, _HOT_RELEASE):

  deployment_log = open("deployment.log", "w")
  if _HOT_RELEASE == "NO":
    command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./manageApp.sh " + _EAR_NAME + " 1 stop; ./deploy.sh " + _EAR_NAME + "; ./manageApp.sh " + _EAR_NAME + " 1 start\" "
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command = cmd.communicate()[0]
    print data_command
    deployment_log.write(data_command)
  elif _HOT_RELEASE == "YES":
    command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deploy.sh " + _EAR_NAME + " 2>&1;\" "
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command = cmd.communicate()[0]
    print data_command
    deployment_log.write(data_command)

  return data_command



def validate_deploy(_EAR_NAME, _IP_ADDRESS):
  command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deploy.sh " + _EAR_NAME + " makeConfig; \" "
  print command
  command_sb = sb.Popen(shlex.split(command), stdout=sb.PIPE)
  data_command = command_sb.communicate()[0]
  print data_command
  return data_command


def getEnvTable():
  os.chdir(WORKSPACE)
  command = "curl -u " + SVNUSER + ":" + SVNPASS + " -X GET http://10.33.20.5:8080/svn/eis/cqm/AutoDeployment/EIS_Environment_List.txt"
  print command
  cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE)
  data_cmd = cmd.communicate()[0]
  return data_cmd


def getIpAddress(_data_cmd):

  # data_cmd = getEnvTable()
  data_cmd = _data_cmd

  group = re.search(ENVIRONMENT + ur'\|([^\|]*)\|[^\|]*', data_cmd)
  if group is not None and len(group.groups()) > 0:
    print group.groups()[0]
    domain = group.groups()[0]

    command = "nslookup " + domain
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_cmd = ""
    data_cmd = cmd.communicate()
    tmp = data_cmd[0].split()[-1]
    if tmp.split() != "":
      global IP_ADDRESS
      IP_ADDRESS = tmp
      
      print IP_ADDRESS
      # return IP_ADDRESS
    else:
      msg = "[ERROR] IP_ADDRESS does not exist from server " + ENVIRONMENT + "\n"
      print msg
      mail.write(msg)
      sys.exit(-1)
  else:
    msg = "[ERROR] IP_ADDRESS does not exist from server " + ENVIRONMENT + "\n"
    print msg
    mail.write(msg)
    sys.exit(-1)


def getSuffix(_data_cmd):
  data_cmd = _data_cmd
  group = re.search(ENVIRONMENT +  ur'\|[^\|]*\|([^\|]*)', data_cmd)
  if group is not None and len(group.groups()) > 0:
    # print group.groups()[0]
    global SUFFIX
    SUFFIX = group.groups()[0]
    print "[INFO] " + SUFFIX + "\n"


def svnCreateBranch(_from, _to):
  parentFolder = "/".join(_to.split("/")[:-2])

  cmd = "svn --username=" + SVNUSER + " --password=" + SVNPASS + " mkdir " + parentFolder + " --parents --non-interactive -m \"creating folder for branch\""
  sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
  data = sb_cmd.communicate()[0]
  msg = "[INFO] svnCreateBranch MKDIR\n" + data
  print msg
  mail.write(msg)
  # mail.flush()

  cmd = "svn --username=" + SVNUSER + " --password=" + SVNPASS + " copy "  + _from + " " + _to + " --non-interactive -m \"creating branch\""
  sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
  data = sb_cmd.communicate()[0]
  msg = "[INFO] svnCreateBranch COPY\n " + data + "\n"
  print msg
  mail.write(msg)
  # mail.flush()



def artiDeleteService(_service, _folder):
  if _folder != "trunk":
    msg = "[INFO] Deleting old files from " + _folder + "\n"
    print msg
    mail.write(msg)
    mail.flush()
    files = getListFiles(_folder, False)
    if files is not None:
      for _file in files:
        print _file['uri']
        if str(_file['uri'][1:]).split("_")[0] == _service:
          # print "/".join(artifactory_server.split("/")[:-4])
          cmd = "curl -X DELETE -u " + ARTIUSER + ":" + ARTIPASS + " " + "/".join(artifactory_server.split("/")[:-4]) + "/"  + repository + "/" + _folder  + str(_file['uri'])
          print "[INFO] " + cmd
          sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
          data_cmd = sb_cmd.communicate()[0]
          print "[INFO] " + data_cmd
    

##################################################################################################
def regressionPack():

  os.chdir(WORKSPACE)
  if os.path.exists("regression.properties") == True:
    os.remove("regression.properties")

  print "[INFO] REGRESSION_TEST = " + REGRESSION_TEST

  if REGRESSION_TEST == "YES":
    os.chdir(WORKSPACE)
    prop = open("regression.properties", "w")
    REGRESSION_TEST_MODULES = getCategories()
    prop.write("REGRESSION_TEST_MODULES="+REGRESSION_TEST_MODULES + "\n")
    prop.write("ENVIRONMENT="+ENVIRONMENT + "\n")
    prop.flush()
    
####################################################################################################



def JIRA_add_comment(url, key, username, password, comment):
  _comment = {}
  _comment['add'] = {}
  _comment['add']['body'] = comment


  _json = {}
  _json['update'] = {}
  _json['update']['comment'] = [_comment]

  command  = "curl -D- -u " + username + ":" + password +"  -X  PUT -d " + "'" + str(json.dumps(_json)) + "' -H \"Content-Type: application/json\" " + url + "/rest/api/2/issue/" + key
  print command
  sb_command = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
  print sb_command.communicate()[0]



# echo "[INFO] backing up existing cfg and ear files before starting a new deployment"
# back_up $IP_ADDRESS  

data_cmd = getEnvTable()
getIpAddress(data_cmd)
getSuffix(data_cmd)

msg = "[INFO] JIRAKEY = " + JIRAKEY + "\n"
print msg
mail.write(msg)

# global servicePath, branchPath, 
global listServicesSVN
listServicesSVN = getAllPaths()
# servicePath = getServicePath(SERVICE, listServicesSVN)
# branchPath = servicePath.replace("trunk", "branches/" + ARTISOURCE)


list = getListFiles(ARTISOURCE)
print list


msg = "[INFO] back_up\n"
print msg
mail.write(msg)
back_up(IP_ADDRESS)


# if promotion then download single service zip file
if ENVIRONMENT.find("PROD") == -1:
  latestFile = getLatestFile(list, SERVICE)
  print latestFile

  promoteToSIT(latestFile, FOLDER)


  os.system("ls -lah")
  os.system("ls -lah ~/.ssh/")
  os.system("w")


  rcfile = latestFile
  print "[INFO] latestFile=" + latestFile
  if VALIDATION_ONLY == "YES":
    rcfile = latestFile.replace("trunk.zip", RC + ".zip")
    os.system("mv " + latestFile + " " + rcfile)

  print "[INFO] rcfile=" + rcfile

  msg = "[INFO] copy_tibco_artifact " + rcfile + " " + ENVIRONMENT + "\n"
  print msg
  mail.write(msg)
  data_copy_tibco_artifact = copy_tibco_artifact(rcfile, IP_ADDRESS, Destination_dir, ENVIRONMENT)
  mail.write(data_copy_tibco_artifact)



if ENVIRONMENT.find("PROD") != -1:
  VALIDATION_ONLY = "LIVE"
  # RC = "LIVE"


if VALIDATION_ONLY == "YES":
  msg = "[INFO] validate_deploy " + SERVICE + "\n"
  print msg
  mail.write(msg)
  _validate_deploy = validate_deploy(SERVICE, IP_ADDRESS)
  mail.write(_validate_deploy)
  if _validate_deploy.lower().find("failed") == -1:
    if ENVIRONMENT == "LS_SIT" or ENVIRONMENT == "LS_UAT":
      msg = "[INFO] Promote to " + ENVIRONMENT +"\n"
      print msg
      mail.write(msg)


      _deploy_module = deploy_module(SERVICE, IP_ADDRESS, "YES").lower()
      print _deploy_module
      mail.write(_deploy_module)
      mail.flush()

      if _deploy_module.find("error") == -1 and _deploy_module.find("fail") == -1 and _deploy_module.find("exception") == -1:

        os.system("rm " + rcfile)
        os.system("mv " + latestFile + ".copy " + rcfile)
        artiDeleteService(SERVICE, RC)
        uploadToFolder(rcfile, RC)
        regressionPack()
      else:
        msg = "[ERROR] Error deploy_module in " + ENVIRONMENT
        print msg
        mail.write(msg)
        mail.flush()
elif VALIDATION_ONLY == "NO":
  msg = "[INFO] deploy_module " + SERVICE + "\n"
  print msg
  mail.write(msg)
  data_deploy_module = deploy_module(SERVICE, IP_ADDRESS, HOT_RELEASE).lower()


  os.chdir(WORKSPACE)
  regressionPack()

  # if os.path.exists("regression.properties") == True:
  #   os.remove("regression.properties")

  # if REGRESSION_TEST == "YES":
  #   os.chdir(WORKSPACE)
  #   prop = open("regression.properties", "w")
  #   REGRESSION_TEST_MODULES = getCategories()
  #   prop.write("REGRESSION_TEST_MODULES="+REGRESSION_TEST_MODULES)
  #   prop.write("ENVIRONMENT="+ENVIRONMENT)
  #   prop.flush()


  # if data_deploy_module.find("error") != -1 or data_deploy_module.find("exception") !=  -1 or data_deploy_module.find("fail") != -1 or data_deploy_module.find("incorrect") != -1:
  #   msg = "[ERROR] Deploy module failed: " + data_deploy_module
  #   print msg
  #   sys.exit(-1)
  print data_deploy_module
  mail.write(data_deploy_module)

  deploy_couchbasescripts(IP_ADDRESS)
  deploy_emsscripts(IP_ADDRESS)

  if JIRAKEY is not None and JIRAKEY != "":
    if data_deploy_module.find("error") == -1 or data_deploy_module.find("exception") ==  -1 or data_deploy_module.find("fail") == -1 or data_deploy_module.find("incorrect") == -1:
    
      comment = """The service {{color:red}}{0}{{color}} has been deployed successfully to {1} ({2}). Details: http://10.33.20.13:8080/jenkins/job/EIS_DevOps/{3}/console""".format(SERVICE, ENVIRONMENT, IP_ADDRESS, BUILD_NUMBER)
      JIRA_add_comment(url="http://10.33.20.21:8080/jira", key=JIRAKEY, username=JIRAUSER, password=JIRAPASSWD, comment=comment)
    else:
    
# copy_tibco_artifact  $artifact  $IP_ADDRESS  $Destination_dir $ENVIRONMENT
elif VALIDATION_ONLY == "LIVE":

  msg = "[INFO] Deploy to LIVE procedure\n"
  print msg
  mail.write(msg)


  data_command = ""
  for item in list:
    print item
    _service = str(item['uri'])[1:].split("_")[0]
    latestFile = str(item['uri'])[1:]
    rcfile = latestFile

    # download ear bundle from artifactory
    promoteToSIT(latestFile, FOLDER)
    msg = "[INFO] copy_tibco_artifact " + rcfile + " " + ENVIRONMENT + "\n"
    print msg
    mail.write(msg)
    data_copy_tibco_artifact = copy_tibco_artifact(latestFile, IP_ADDRESS, Destination_dir, ENVIRONMENT)
    mail.write(data_copy_tibco_artifact)
    print data_copy_tibco_artifact


    print "[INFO] Service = " + _service

    msg = "[INFO] 1. Validate_deploy LIVE: " + _service + "\n"
    print msg
    mail.write(msg)

    # validate_deploy_result = validate_deploy(SERVICE, IP_ADDRESS).lower()
    validate_deploy_result = validate_deploy(_service, IP_ADDRESS).lower()
    if (validate_deploy_result.find("fail") == -1) and (validate_deploy_result.find("error") == -1) and (validate_deploy_result.find("exception")):
      msg = "[INFO] 2. Deploy_module LIVE: " + _service + "\n"
      print msg
      mail.write(msg)
      # data_command = deploy_module(SERVICE, IP_ADDRESS, HOT_RELEASE).lower()
      data_command += deploy_module(_service, IP_ADDRESS, HOT_RELEASE).lower() + "\n"




  mail.write(data_command)
  print data_command
  msg = "[INFO] 3. Looking for exceptions and errors\n"
  print msg
  mail.write(msg)

  if data_command.find("error") == -1 and data_command.find("exception") == -1 and data_command.find("fail") == -1:
    for item in list:
      _service = str(item['uri'])[1:].split("_")[0]
      msg = "[INFO] Promote to LIVE: " + _service +"\n"
      print msg
      mail.write(msg)
      # latestFile = getLatestFile(list, _service)
      latestFile = str(item['uri'])[1:]
      print "[INFO] latestFile = " + latestFile
      rcfile = latestFile

      # revert backed-up zip file
      os.system("rm " + rcfile)
      os.system("mv " + latestFile + ".copy " + rcfile)
      # delete EMS and COUCHBASE BEFORE UPLOADING TO ARTIFACTORY
      os.system("zip -d Ems.tar " + rcfile)
      os.system("zip -d Couchbase.tar " + rcfile)
      artiDeleteService(_service, RC)
      uploadToFolder(rcfile, RC)

      
      servicePath = getServicePath(_service, listServicesSVN)
      branchPath = servicePath.replace("trunk", "branches/" + ARTISOURCE)
      print "[INFO] Branch to create: " + branchPath

      svnCreateBranch(servicePath, branchPath)
    
  else:
    print data_command
    msg = "[ERROR] FOUND ERRORS DURING LIVE PROCESS, PLEASE CHECK LOG!!!"
    print msg
    mail.write(msg)
    sys.exit(-1)



# properties.write("ENVIRONMENT=" + ENVIRONMENT)






# deploy_couchbasescripts  $IP_ADDRESS $COUCHBASE_SCRIPTS 2>&1 | tee deploy_couchbasescripts.log





# deploy_emsscripts  $IP_ADDRESS $EMS_SCRIPTS 2>&1 | tee deploy_emsscripts.log








