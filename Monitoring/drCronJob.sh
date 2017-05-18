#!/bin/bash
result=$(sudo crontab -l | grep drRunMonitoring.sh)
if [ "$?" -ne 0 ]
then
    sudo chmod +x /app/cqm_dr/drRunMonitoring.sh
    sudo crontab -l > mycron
    sudo touch /app/cqm_dr/output.log
    sudo chmod ugo+rw /app/cqm_dr/output.log
	sudo echo "*/1 * * * * /app/cqm_dr/drRunMonitoring.sh >> /app/cqm_dr/output.log" >> mycron
	sudo crontab mycron
	sudo rm mycron

fi