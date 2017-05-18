#!/bin/bash -x

. ../Library/CQM_lib.sh

rm -rf *

############################################################
# Set number of nodes and ip addresses for the target
# environment
############################################################


SET_ENV_VARIABLES () {


case "${ENVIRONMENT}" in
     "LS_DEV")
          NUMBER_NODES=1
          NODE_IP[1]="10.35.104.27"
          ;;
	 "LS_UAT")
          NUMBER_NODES=1
          NODE_IP[1]="10.35.108.40"
          echo ${ENVIRONMENT} > regression.properties
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
          echo ${ENVIRONMENT} > regression.properties
          ;;
          
     "SW_PROD")
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

CONFIGURATION_FILE_URL="http://10.33.20.5:8080/svn/api_remotebetslip_with_btk/configuration/${ENVIRONMENT}/"

svn export --username CQMSVN --password $svnpwd --non-interactive $CONFIGURATION_FILE_URL

file1=./${ENVIRONMENT}/config.js
file2=./${ENVIRONMENT}/config_RBS.js

if [ ! -e "$file1" ]; 
then

    echo "$file1 does not exist for the ${ENVIRONMENT} environment, please check SVN!"
    exit 1;
    
fi 

if [ ! -e "$file2" ]; 
then
    echo "$file2 does not exist for the ${ENVIRONMENT} environment, please check SVN!"
    exit 1;
fi 
}

############################################################
#  Download the latest or the norminated artifact 
# from artifactory
############################################################

GET_ARTIFACT_FROM_FACTORY () {

if [ -z "$RELEASECANDIDATE" ]; then
    if [ -z "$custom_artifact" ]; then
         echo "[ERROR] : Invalid parameters! Please check buildsource or custom_artifact"
         exit 1;
    else
         ARTIFACT=$custom_artifact
         branch=`echo $ARTIFACT | cut -d'.' -f4`
    fi
else
    branch=${RELEASECANDIDATE}
    FOLDER_URL="http://10.33.20.7:8080/artifactory/api/storage/API/${branch}/"
    curl -X GET $FOLDER_URL > files.json
    ARTIFACT=$(cat files.json | grep uri | grep RBS_REV | grep tar | sort -t. -k3 -n |tail -n1 | cut -d'"' -f4 | cut -d"/" -f2)
    MINARTI="MIN"${ARTIFACT}
    NONMINARTI="NONMIN"${ARTIFACT}
fi

revision=`echo $ARTIFACT | cut -d'.' -f3`
artifact_url="http://10.33.20.7:8080/artifactory/API/$branch/$ARTIFACT"
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
	rm -f ${ARTIFACT} ${NONMINARTI}
    mv ${MINARTI} ${ARTIFACT}

else
	rm -f ${ARTIFACT} ${MINARTI}
    mv ${NONMINARTI} ${ARTIFACT}
fi

}

test_deploy_RBS () {
    echo $NUMBER_NODES
   for i in `seq 1 $NUMBER_NODES`;
   do
     echo ${NODE_IP[i]}
   done
  
    deployment_dir=/var/tmp/test/api
    working_dir=/var/tmp/test/api_deploy
    mkdir -p $deployment_dir
    mkdir -p $working_dir
    cp $ARTIFACT $working_dir
    tar xvf $working_dir/$ARTIFACT -C  $deployment_dir
    rm -rf $deployment_dir $working_dir
}

deploy_RBS () {
   
if [ $NUMBER_NODES -eq 1 ]; then
   echo "[INFO] : There is 1 node in this environment"
else
   echo "[INFO] : There are $NUMBER_NODES nodes in this environment"
fi  
   for IP_ADDRESS in "${NODE_IP[@]}";
   do 
      echo "[INFO] : Deploying $ARTIFACT to node $IP_ADDRESS" 
      deployment_dir="/var/tmp/test/api"
      tomcat_dir="/apps/tomcat7/webapps"
      
      ssh -i ~/.ssh/api_id_rsa   apideploy@$IP_ADDRESS -C "rm -rf $deployment_dir; mkdir -p ${deployment_dir}; cd ${deployment_dir}; mkdir -p API_RBS_${branch}_${revision}"
      ls
      echo $ARTIFACT 
      scp -i ~/.ssh/api_id_rsa   $ARTIFACT ${ENVIRONMENT}/*.js apideploy@$IP_ADDRESS:${deployment_dir}/
      ssh -i  ~/.ssh/api_id_rsa  apideploy@$IP_ADDRESS -C "cd ${tomcat_dir}; rm -rf RemoteBetslip; mkdir temp; cp ${deployment_dir}/$ARTIFACT ./temp/; cd temp; tar xvf $ARTIFACT; chmod o+rx -R RemoteBetslip; cp -r RemoteBetslip ../; cd ..; cp ${deployment_dir}/*.js ${tomcat_dir}/RemoteBetslip/bets/js/; rm -rf temp;"  

   done 
echo "[INFO] : Deployment finished"
}

crap() {
echo "Backing up existing configuration...clear previous backups"   
rm -f $(ls -1t ${deppath}/backup/ | tail -n +11)
zip -r ${deppath}/backup/RBS_`date +%Y%m%d-%H%M`.zip ${deppath}/.
echo "Copy Artifacts to Server (${ip_addres})"
cp $fname ${deppath}
echo "Deploying the latest code..."
unzip -o ${deppath}/$fname -d ${deppath}

}



if [ ! -z "$JIRAKEY" ]; then
    echo "<br>This API deployment was triggered from ticket <a href="https://tools.ladbrokes.com/jira/browse/$JIRAKEY">$JIRAKEY</a>."  >> Mail.txt
else 
    echo "<br>This API deployment was triggered from Jenkins."  >> Mail.txt
fi

SET_ENV_VARIABLES
echo "<br><b>API MODULE: </b> RBS<br>" >> Mail.txt
echo "<br><b>Environment: </b>${ENVIRONMENT}<br>" >> Mail.txt
GET_CONFIGURATION 
echo "<br><b>Configuration files: </b> ${CONFIGURATION_FILE_URL}<br>" >> Mail.txt


if [ ${MINIFICATION} == 'Y' ]
then
       	
	Minify=Minified
    
else
    	
	Minify=Non-Minified
fi

#Ensure that Minified code is deployed in PROD##

if [[ ${ENVIRONMENT} == 'SW_PROD' &&  ${MINIFICATION} == 'N' ]]
then
    echo "ERROR!!! You are deploying non-Minified code to PROD Environment ${ENVIRONMENT} " 
	exit 1;
    
fi   
 
    
echo "<br><b>Minify      : </b> ${MINIFICATION}" >> Mail.txt
echo "<br><b>Environment : </b> ${ENVIRONMENT}" >> Mail.txt
echo "Deploying ${Minify} code to ${ENVIRONMENT}" >>  Mail.txt
	
GET_ARTIFACT_FROM_FACTORY 
    
SELECTWAR
    
echo "<br><b>Artefact: </b> $artifact_url" >> Mail.txt
deploy_RBS

echo "<b><br><br><br>For Detailed deployment log, please refer to the following URL: <br><br> http://jira.ladbrokes.co.uk/jenkins/view/API/job/$JOB_NAME/$BUILD_NUMBER/console" >> Mail.txt

########################################################################
#### Promote the latest Artifact from trunk to the Release Candidate ###
########################################################################

if [ ${ENVIRONMENT} == 'SW_PROD' ] 
then

	Promote_Latest_Artifact API ${RELEASECANDIDATE} LIVE RBS ${ARTIPWD}
fi


############################################################################
# Cleanup
############################################################################
#rm -rf $ARTIFACT

