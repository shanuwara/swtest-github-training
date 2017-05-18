#!/bin/bash
result=$(sudo ls /app/cqm_dr/Monitoring)
if [ "$?" -ne 0 ]
then
   svn co   http://10.33.20.5:8080/svn/cqm/cqm_tools/Monitoring   /app/cqm_dr/Monitoring      --username cqmsvn --password K_29^ob  --non-interactive 
fi	
result=$(sudo ls /app/cqm_dr/cqm)
if [ "$?" -ne 0 ]
then
   svn co   http://10.33.20.5:8080/svn/cqm/cqm_tools/python_library/cqm   /app/cqm_dr/cqm      --username cqmsvn --password K_29^ob  --non-interactive 
fi

svn up  /app/cqm_dr/Monitoring      --username cqmsvn --password K_29^ob  --non-interactive

svn up  /app/cqm_dr/cqm             --username cqmsvn --password K_29^ob  --non-interactive


/usr/local/bin/python  /app/cqm_dr/cqm/connectivity.py http://10.33.20.14:8055/api/dr/connectivity  /app/cqm_dr/Monitoring/server-config.json >> /app/cqm_dr/output.log 2>&1
/usr/local/bin/python  /app/cqm_dr/cqm/serviceConnectivity.py http://10.33.20.14:8055/api/dr/service  /app/cqm_dr/Monitoring/server-config.json >> /app/cqm_dr/output.log 2>&1