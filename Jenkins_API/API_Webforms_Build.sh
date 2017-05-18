#!/bin/bash

set -x

rm -rf *.properties

. ../Library/CQM_lib.sh



#export REV=`svn --username $scmuser --password $scmpwd --non-interactive info  $svnurl |grep "Last Changed Rev:" |cut -c19-`O


#echo "Build Initiated with SVN Revision : " $REV

ARTIFACT_NAME="WebForms_REV_${SVN_REVISION}_BUILD_${BUILD_NUMBER}_trunk.tar"

mv ./WebForms/dist/forms.tar ${ARTIFACT_NAME}


Artifactory_deploy_artifact ${ARTIFACT_NAME} "http://10.33.20.7:8080/artifactory/API/trunk" "admin" $artipwd

echo "ENVIRONMENT=LS_DEV" > LS_DEV.properties
echo "RELEASECANDIDATE=trunk" >> LS_DEV.properties

