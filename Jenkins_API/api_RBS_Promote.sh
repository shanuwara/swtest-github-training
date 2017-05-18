#!/bin/bash -x

. ../Library/CQM_lib.sh

##########################################################
###       Validate the Release Candidate Name          ###
##########################################################

if [[ ${RELEASECANDIDATE} == "null" || ${RELEASECANDIDATE} == '' ]]
then
	echo "Release Candidate set to null, please enter a valid Release Candidate name"
    exit 1;
fi

##########################################################
###   Delete previous version RBS in Release Candidate ###
##########################################################

curl -X GET "http://10.33.20.7:8080/artifactory/api/storage/API/${RELEASECANDIDATE}/" > ${JIRAKEY}_${RELEASECANDIDATE}.json

if [ $(cat ${JIRAKEY}_${RELEASECANDIDATE}.json |grep uri | grep 'RBS_REV' | wc -l) -ne 0 ]
then
	echo "RBS Exists in the ${RELEASECANDIDATE}. Deleting old RBS versions."
    
    cat ${JIRAKEY}_${RELEASECANDIDATE}.json | grep uri | grep 'RBS_REV' | 
          egrep  "tar" | cut -d'"' -f4 | cut -d"/" -f2 > Delete_Artifacts.lst
    
    for file in `cat Delete_Artifacts.lst`
    do
    	echo "Deleting ${file} from ${RELEASECANDIDATE} "
        curl -u "admin":"${ARTIPWD}" -X DELETE "http://10.33.20.7:8080/artifactory/API/${RELEASECANDIDATE}/${file}"
    done
fi

##############################################
## Get The latest version of the Artifact ####
##############################################

curl -X GET "http://10.33.20.7:8080/artifactory/api/storage/API/trunk/" > ${BUILD_NUMBER}_ARTIFACTS.json

ARTIFACT=$(cat ${BUILD_NUMBER}_ARTIFACTS.json | grep 'RBS_REV' | grep uri |egrep  "tar" | sort -t_ -k3 -k5 -nr | head -1 | cut -d'"' -f4 | cut -d"/" -f2)
MINARTI="MIN"${ARTIFACT}
NONMINARTI="NONMIN"${ARTIFACT}

echo "ARTIFACT     : ${ARTIFACT}"
echo "MINI-ARTI    : ${MINARTI}"
echo "NON-MINI ARTI: ${NONMINARTI}"


ARTIFACT_URL="http://10.33.20.7:8080/artifactory/API/trunk/${ARTIFACT}"

wget ${ARTIFACT_URL}

RC_NAME=$(echo ${ARTIFACT} | sed "s/trunk/${RELEASECANDIDATE}/g" )
MINRC=$(echo "MIN"${ARTIFACT} | sed "s/trunk/${RELEASECANDIDATE}/g" )
NONMINRC=$(echo "NONMIN"${ARTIFACT} | sed "s/trunk/${RELEASECANDIDATE}/g" )
RC_URL="http://10.33.20.7:8080/artifactory/API/${RELEASECANDIDATE}/${RC_NAME}"

############################################################################
### Rename the Minified and Non-minified code within the ARTIFACT as well ##
############################################################################
tar -xvf ${ARTIFACT}
mv ${MINARTI} ${MINRC}
mv ${NONMINARTI} ${NONMINRC}


tar -cvf ${RC_NAME} ${MINRC} ${NONMINRC}


#mv ${ARTIFACT} ${RC_NAME}

Artifactory_deploy_artifact ${RC_NAME} "http://10.33.20.7:8080/artifactory/API/${RELEASECANDIDATE}" "admin" ${ARTIPWD}

(
    echo "<br>API Job      :</b> API Promote RBS"
    echo "<br>Triggered by :</b><a href="https://tools.ladbrokes.com/jira/browse/${JIRAKEY}">$JIRAKEY</a>." 
    echo "<br><b>Promoting Artifact:</b>${ARTIFACT} "
    echo "<br><b>    From     :</b>${ARTIFACT_URL} "
    echo "<br><b>    To       :</b>${RC_URL} "
    
 ) > Mail.txt
