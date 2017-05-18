#!/bin/bash -x

. ../Library/CQM_lib.sh

rm -rf *

echo "Start Time: $(date)"

############################################################
# Set number of nodes and ip addresses for the target
# environment
############################################################


SET_ENV_VARIABLES () {

CONFIGURATION_FILE=/usr/private/registration.properties

case "${ENVIRONMENT}" in
     "LS_DEV")
          NUMBER_NODES=1
          NODE_IP[1]="10.35.104.27"
          ;;
     "LS_UAT")
          NUMBER_NODES=1
          NODE_IP[1]="10.35.108.40"
          ;;
     "RL_UAT")
          NUMBER_NODES=1
          NODE_IP[1]="10.192.172.27"
          ;;           
     "LS_SANDBOX")
          NUMBER_NODES=1
          NODE_IP[1]="10.35.14.7"
          ;;
     "LS_PERF")
          NUMBER_NODES=4
          NODE_IP[1]="10.35.18.32"
          NODE_IP[2]="10.35.18.33"
          NODE_IP[3]="10.35.18.34"
          NODE_IP[4]="10.35.18.35"
          ;;
     "SW_PROD")
          NUMBER_NODES=4
          NODE_IP[1]="10.33.22.27"
          NODE_IP[2]="10.33.22.28"
          NODE_IP[3]="10.33.22.29"
          NODE_IP[4]="10.33.22.30"
          ;;
esac
}


############################################################
# Download the configuration file according to the Environment
############################################################

GET_CONFIGURATION () {

CONFIGURATION_FILE_URL="http://10.33.20.5:8080/svn/api_webform/configuration/${ENVIRONMENT}/registration.properties"

svn export --username CQMSVN --password $svnpwd --non-interactive http://10.33.20.5:8080/svn/api_webform/configuration/${ENVIRONMENT}/registration.properties
file=./registration.properties
if [ ! -e "$file" ]; then
    echo "registration.properties file does not exist for the ${ENVIRONMENT} environment, please check SVN!"
    exit 1;
fi 
}

############################################################
#  Download the latest or the nominated artifact 
# from artifactory
############################################################

GET_ARTIFACT_FROM_FACTORY () {

if [ -z "${RELEASECANDIDATE}" ]; then 
   	if [ -z "$custom_artifact" ]; then
         echo "[ERROR] : Invalid parameters! Please check buildsource or custom_artifact"
         exit 1;
    else
         ARTIFACT=${custom_artifact}
         branch=`echo ${ARTIFACT} | cut -d'.' -f4`
      
    fi
    
else
    branch=${RELEASECANDIDATE}
    FOLDER_URL="http://10.33.20.7:8080/artifactory/api/storage/API/${branch}"
    curl -X GET $FOLDER_URL > files.json
    ARTIFACT=$(cat files.json | grep WebForms_REV | grep uri | grep tar | sort -t. -k6 -k3 -n | tail -n1 | cut -d'"' -f4 | cut -d"/" -f2)

fi

revision=`echo $ARTIFACT | cut -d'.' -f3`
artifact_url="http://10.33.20.7:8080/artifactory/API/${branch}/${ARTIFACT}"
echo "[INFO] :  Downloading $ARTIFACT from artifactory to `pwd`"
wget $artifact_url
echo "[INFO] : Download completed"

}


################################################################################
## Select the relevant (Minified or Non-Minified) file from the tar artifact  ##
################################################################################
SELECTWAR () {

tar xvf ${ARTIFACT}

if [ ${MINIFICATION} == 'Y' ]
then
	rm -f forms.war
    mv mini-forms.war forms.war

else
	rm -f mini-forms.war
fi

}


test_deploy_WebForms () {
    
   echo $NUMBER_NODES
   
   for i in `seq 1 $NUMBER_NODES`;
   do
   
   	echo ${NODE_IP[i]}
   
   done
  
    deployment_dir=/var/tmp/test/api
    working_dir=/var/tmp/test/api_deploy
    mkdir -p $deployment_dir
    mkdir -p $working_dir
    cp form.war $working_dir
    tar xvf $working_dir/forms.war -C  $deployment_dir
    rm -rf $deployment_dir $working_dir
}


###########################################################
# deploying Webforms to tomcat and restart tomcat instance
###########################################################
deploy_WebForms () {
   
if [ $NUMBER_NODES -eq 1 ]; then
   echo "[INFO] : There is 1 node in this environment"
else
   echo "[INFO] : There are $NUMBER_NODES nodes in this environment"
fi  
   for IP_ADDRESS in "${NODE_IP[@]}";
   do 
      deployment_dir="/var/tmp/test/api"
      tomcat_home="/apps/tomcat7"
      tomcat_dir="/apps/tomcat7/webapps"

      echo "[INFO] : Shutting down tomcat on node $IP_ADDRESS"
      ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C "sudo /etc/init.d/tomcat7 stop"

      echo "[INFO] : Doing Backup of existing application on node $IP_ADDRESS"
      back_up "$tomcat_dir" "$IP_ADDRESS"
      echo "[INFO] : Backing up completed!" 

      echo "[INFO] : setting proper permission to directories:"
      ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C  "sudo /bin/chgrp -R webadms /apps/tomcat7/webapps" 
      ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C  "sudo /bin/chgrp -R webadms /apps/tomcat7/work"
      ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C  "sudo /bin/chmod -R g+w  /apps/tomcat7/webapps" 
      ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C  "sudo /bin/chmod -R g+w /apps/tomcat7/work"
 
     echo "[INFO] : Clearing work directory" 
     ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C "cd $tomcat_home/work/Catalina/localhost; rm -rf forms"

      echo "[INFO] : Deleting current application"
      ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C "cd $tomcat_dir; rm -rf forms.war forms"

      echo "[INFO] : Deploying $ARTIFACT to node $IP_ADDRESS and restarting tomcat" 

      #rm -rf $deployment_dir
      ssh -i /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C "mkdir -p ${deployment_dir}; cd ${deployment_dir}; mkdir -p API_WebForms_${branch}_${revision}"
      ls
      echo $ARTIFACT 
      scp -i /home/jenkinsci/.ssh/api_id_rsa  $ARTIFACT forms.war registration.properties apideploy@$IP_ADDRESS:${deployment_dir}/
      ssh -i /home/jenkinsci/.ssh/api_id_rsa  apideploy@$IP_ADDRESS -C "cd ${tomcat_dir}; cp -p ${deployment_dir}/forms.war . ; chmod 777 forms.war; sudo /bin/chgrp webadms $CONFIGURATION_FILE; cat ${deployment_dir}/registration.properties > $CONFIGURATION_FILE; sudo /etc/init.d/tomcat7 start"  
        
   done 
echo "[INFO] : Deployment finished"
}

#########################################################
## If deployed to PROD keep copy in Artifactory live ####
#########################################################

if [ ${ENVIRONMENT} == 'SW_PROD' ]
then

	echo "Release Candidate : ${RELEASECANIDATE}"


    Promote_Latest_Artifact API ${RELEASECANDIDATE} LIVE WebForms ${ARTIPWD}

fi


###########################################################
# backing up Configuration files and the application in tomcat
###########################################################

back_up () {
   tomcat_dir=$1
   IP_ADDRESS=$2
   backup_dir=/var/tmp/api
   backup_file=API_DEPLOYMENT_BACKUP_$BUILD_NUMBER.tar
   
   ssh -i  /home/jenkinsci/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C "mkdir -p $backup_dir; tar cvf $backup_file  $tomcat_dir/forms; mv $backup_file $backup_dir/; cp $CONFIGURATION_FILE $backup_dir/"
}

if [ ! -z "$JIRAKEY" ]; then
    echo "<br>This API deployment was triggered from ticket <a href="https://tools.ladbrokes.com/jira/browse/$JIRAKEY">$JIRAKEY</a>."  >> Mail.txt
else 
    echo "<br>This API deployment was triggered from Jenkins."  >> Mail.txt
fi

echo "<br><b>API MODULE: </b> WebForms<br>" >> Mail.txt
SET_ENV_VARIABLES


echo "<br><b>Environment: </b>${ENVIRONMENT}<br>" >> Mail.txt
GET_CONFIGURATION 
echo "<br><b>Configuration file: </b> $CONFIGURATION_FILE_URL<br>" >> Mail.txt

if [ ${MINIFICATION} == 'Y' ]
then
       	
	Minify=Minified
    
else
    	
	Minify=Non-Minified
fi

#Ensure that Minified code is deployed in PROD##

if [[ ${ENVIRONMENT} == 'SW_PROD' && ${MINIFICATION} == 'N' ]]
then
        echo "ERROR!!! You are deploying non-Minified code to PROD Environment ${ENVIRONMENT} " 
exit 1;


else
    
	echo "<br><b>Minify      : </b> ${MINIFICATION}" >> Mail.txt
    echo "<br><b>Environment : </b> ${ENVIRONMENT}" >> Mail.txt
    echo "Deploying ${Minify} code to ${ENVIRONMENT}" >>  Mail.txt
	
    GET_ARTIFACT_FROM_FACTORY 
	
    SELECTWAR
	
    echo "<br><b>Artifact: </b> $artifact_url" >> Mail.txt
	#test_deploy_WebForms
	deploy_WebForms

	echo "<b><br><br><br>For Detailed deployment log, please refer to the following URL: <br><br> http://jira.ladbrokes.co.uk/jenkins/view/API/job/$JOB_NAME/$BUILD_NUMBER/console" >> Mail.txt

fi

############################################################################
# Cleanup
############################################################################
#rm -rf $ARTIFACT

echo "End Time : $(date) "
