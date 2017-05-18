#!/bin/bash -x

# This code snippet sets the SVN revision number before initiating builds, to indicate clearly the SVN revision used 
# to create the build


. ../Library/CQM_lib.sh


export YUI=${WORKSPACE}/../Library/yuicompressor

export BETS=RemoteBetslip/bets
export MINBETS=RemoteBetslip/minbets
export TLKT=RemoteBetslip/toolkit
export MINTLKT=RemoteBetslip/mintoolkit

export BLD="RBS_REV_${SVN_REVISION}_BUILD_${BUILD_NUMBER}_trunk.tar"

export MINBLD="MIN"${BLD}
export NONMINBLD="NONMIN"${BLD}

#svn export --username $scmuser --password $scmuserpwd --non-interactive $svnurl

(
 echo "Start Time: $(date)"

################################################################
######### Creating Both Minified and Non-Minified build ########
################################################################


cp -r ${BETS} ${MINBETS}
cp -r ${TLKT} ${MINTLKT}

find ${BETS} -name "*.js"  -print | grep -v lib > bets_js.lst
find ${BETS} -name "*.css" -print | grep -v lib > bets_css.lst
find ${TLKT} -name "*.js"  -print | grep -v lib > toolkit_js.lst
find ${TLKT} -name "*.css" -print | grep -v lib > toolkit_css.lst

for file in `cat bets_js.lst` `cat bets_css.lst`
do
        newfile=$(echo $file | sed 's/\/bets\//\/minbets\//g' )
        java -jar ${YUI}/yuicompressor-2.4.9.jar ${file} --nomunge -o ${newfile}

done

for file in `cat toolkit_js.lst` `cat toolkit_css.lst`
do
        newfile=$(echo $file | sed 's/\/toolkit\//\/mintoolkit\//g' )
        java -jar ${YUI}/yuicompressor-2.4.9.jar ${file} --nomunge -o ${newfile}

done

## Create tar of full code
tar -zvcf ${NONMINBLD}  --exclude=RemoteBetslip/min* RemoteBetslip

## Create tar for minified code.

rm -r ${BETS}
rm -r ${TLKT}

mv ${MINBETS} ${BETS}
mv ${MINTLKT} ${TLKT}
tar -zvcf ${MINBLD} RemoteBetslip

#Tar both the minified and nonminified to create the Artifact 
tar cvf $BLD ${MINBLD} ${NONMINBLD}
     
echo "<br> ${BLD} Build created " > Mail.txt
     
Artifactory_deploy_artifact $BLD "http://10.33.20.7:8080/artifactory/API/trunk" "admin" $artipwd


echo "CI Build ${BLD} uploaded to Artifactory"
echo "<br>CI Build ${BLD} uploaded to Artifactory " >> Mail.txt

echo "ENVIRONMENT=LS_DEV" > LS_DEV.properties
echo "RELEASECANDIDATE=trunk" >> LS_DEV.properties


#rm -rf *.tar
#rm -f *.lst

echo "End Time : $(date) "

) | tee test-${BUILD_NUMBER}.log 2>&1


if [ $(cat test-${BUILD_NUMBER}.log | egrep -i ' error |error |denied|failed' | wc -l) -ne 0 ]
then
     echo "ERROR!!! API_RBS_Build ${BUILD_NUMBER} Job may have FAILED. Please check the full log"
     echo "<br><b>ERROR within the build </b>" >> Mail.txt
