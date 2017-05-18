#!/bin/bash -x


. ../Library/CQM_lib.sh


rm -rf *.*
echo "API Trigger jobs started at: $(date)" > Mail.txt

#(
echo "Start Time: $(date)"

###############################################################################
#retrieving information from the JIRA ticket which comes back as a JSON file
###############################################################################
curl -u ${JIRAUSERNAME}:${JIRAPWD}  -X GET http://10.33.20.21:8080/jira/rest/api/2/issue/${JIRAKEY}/ > ${JIRAKEY}.json


JIRAUSER=$(cat ${JIRAKEY}.json | jq -r '.fields.reporter.displayName' )
JIRAMAIL=$(cat ${JIRAKEY}.json | jq -r '.fields.reporter.emailAddress' )
JIRADESC=$(cat ${JIRAKEY}.json | jq -r '.fields.issuetype.description' )
JIRAENV=$(cat  ${JIRAKEY}.json | jq -r '.fields.customfield_11913.value' )
JIRAMINI=$(cat ${JIRAKEY}.json | jq -r '.fields.customfield_12103.value' )
JIRASERV=$(cat ${JIRAKEY}.json | jq -r '.fields.customfield_11911.value' )
JIRARC=$(cat   ${JIRAKEY}.json | jq -r '.fields.customfield_11912' )
JIRATYPE=$(cat ${JIRAKEY}.json | jq -r '.fields.issuetype.id' )

#################################################
# Issue Type is Promote
#################################################

if [ ${JIRATYPE} == "10900" ] 
then
    JOBTYPE="API_Promote"
    _TYPE="promote"
    _RC=${JIRARC}
    
    if [ ${JIRASERV} != "WebForms" -a ${JIRASERV} != "RBS" ]
	then
    	  echo "Invalid deployment parameters!"
          exit 1;
    fi
    
(

echo "JIRAKEY=${JIRAKEY}" 
echo "ENVIRONMENT=${JIRAENV}" 
echo "MINIFICATION=${JIRAMINI}" 
echo "_TYPE=${_TYPE}" 
echo "API_MODULE=${JIRASERV}" 
echo "RELEASECANDIDATE=${JIRARC}"
echo "_RC=${_RC}"
echo "_ENVIRONMENT=${JIRAENV}"
echo "_SERVICE=${JIRASERV}"

) > ${JOBTYPE}_${JIRASERV}.properties 



#################################################
# Issue Type is Deploy
#################################################

elif [ ${JIRATYPE} == "10800" ]
then
    JOBTYPE="API_Deploy";   
    _TYPE="deploy"
    _RC=${JIRARC}
    
	curl -X GET "http://10.33.20.7:8080/artifactory/api/storage/API/${JIRARC}/" | 
          grep uri | egrep  'RBS|WebForms' | cut -d'"' -f4 | cut -d"/" -f2 | cut -d"_" -f1 | sort | uniq > services.lst
            


for service in `cat services.lst`
do

(
echo "JIRAKEY=${JIRAKEY}" 
echo "ENVIRONMENT=${JIRAENV}" 
echo "_ENVIRONMENT=${JIRAENV}" 
echo "_TYPE=${_TYPE}" 
echo "MINIFICATION=${JIRAMINI}" 
echo "API_MODULE=${service}" 
echo "_SERVICE=${service}"
echo "RELEASECANDIDATE=${JIRARC}"
echo "_RC=${_RC}"

) > ${JOBTYPE}_${service}.properties

done
#################################################
# Issue Type is Build
#################################################

elif [ ${JIRATYPE} == "26" ]
then
    JOBTYPE="API_Build"
    _TYPE="build"
    
    if [ "${JIRASERV}" == "Gateway" ]
    then
    
(
echo "JIRAKEY=${JIRAKEY}" 
echo "ENVIRONMENT=${JIRAENV}" 
echo "_TYPE=${_TYPE}" 
echo "API_MODULE=${JIRASERV}" 
echo "_ENVIRONMENT=${JIRAENV}"
echo "_SERVICE=${JIRASERV}"

) > ${JOBTYPE}_${JIRASERV}.properties  
    
    
    else
		echo "Build Issue Type selected. Builds are not triggered using JIRA!"
 		exit 1;
	fi
fi




#) | tee test-${BUILD_NUMBER}.log 2>&1

cat  ${JOBTYPE}_*.properties >> Mail.txt


#if [ $(cat test-${BUILD_NUMBER}.log | egrep -i ' error |error |denied|failed' | wc -l) -ne 0 ]
#then
#     echo "ERROR!!! Build Job may have FAILED. Please check the full log"
#     echo "<br><b>ERROR within the build" >> Mail.txt
#fi
#
#echo "API Trigger Job Ended at: $(date)" >> Mail.txt
