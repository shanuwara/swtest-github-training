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


########################################################################
#### Promote the latest Artifact from trunk to the Release Candidate ###
########################################################################
Promote_Latest_Artifact API trunk ${RELEASECANDIDATE} WebForms ${ARTIPWD}

####################
#### Send Emails ###
####################
(
    echo "<br>API Job      :</b> API Promote WebForms"
    echo "<br>Triggered by :</b><a href="https://tools.ladbrokes.com/jira/browse/${JIRAKEY}">$JIRAKEY</a>." 
    echo "<br><b>Promoting Artifact:</b>${ARTIFACT} "
    echo "<br><b>    From     :</b>${ARTIFACT_URL} "
    echo "<br><b>    To       :</b>${RC_URL} "
    
 ) > Mail.txt


#rm ${JIRAKEY}_${RELEASECANDIDATE}.json 
#rm Delete_Artifacts.lst
#rm ${BUILD_NUMBER}_ARTIFACTS.json
