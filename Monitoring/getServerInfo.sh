#!/bin/bash 

function  checkConnectivity()
{
ServerIP=$1
ServerPort=$2
nc -z -v -w5 ${ServerIP} ${ServerPort}
if [ "$?" -ne 0 ]
then
       echo "{\"port\":$ServerPort,\"status\":\"failed\"}"
else 
       echo "{\"port\":$ServerPort,\"status\":\"succeeded\"}"
fi
}


function checkService()
{
result=$(ps -ef | grep $1  | grep -v grep)
[ $?  -eq "0" ] && echo "{\"service\":\"$1\",\"status\":\"running\"}" || echo "{\"service\":\"$1\",\"status\":\"not running\"}"

}
function getDiskSpace()
{
# df -H |  grep -vE '^Filesystem|tmpfs|cdrom' 
#result=$(df -H |  grep -vE '^Filesystem|cdrom' | awk '{ printf("{\"name\":\"%s\",\"total\":\"%s\",\"free\":\"%s\"}\n",$1,$2,$2-$4)}' | paste -sd "," - )
#result=$(df -h  |  grep -vE '^Filesystem|cdrom' | awk '{ if($6=="/app" || $6=="/var") { printf("{\"name\":\"%s\",\"total\":\"%s\",\"free\":\"%s\",\"%ageUsed\":\"%s\"}\n",$6,$2,$3,$4)} }' | paste -sd "," - )
result=$(df -h  |  grep -vE '^Filesystem|cdrom' | awk '{ if($5=="/app" || $5=="/var") { printf("{\"name\":\"%s\",\"total\":\"%s\",\"free\":\"%s\",\"%ageUsed\":\"%s\"}\n",$5,$1,$3,$4)} }' | paste -sd "," - )
#df -PH | awk '{if ($6=="/app" || $6=="/var") printf("%s   %s  %s  %s \n",$1,$2, $3, $6)}'
#diskContent=$(cat diskContent.txt |paste -sd "," -)
#diskResult=$(convertToJson "$result")
echo "[$result]"
}

function availDiskSpace()
{ 

#IDX=$(df -h /var | head -1 | sed 's/$/|/g' | awk 'BEGIN{FS="|";OFS="|"} { print index($1, "Use%" ), "" }' | sed 's/|//g' )

for disk in var \
            app
do
	freq=FALSE

	perFree=$(df -h /${disk} |  grep -vE '^Filesystem|cdrom' | tail -1 | awk '{ printf("%s\n", $4) }' | sed 's/%//g' )
        echo "Percentage Free: $perFree"
       
        if [ ${perFree} -ge 90 ]
  	then
	   	freq=TRUE
        fi
done

}

function getRam()
{
 
#cpuResult=$(echo {'"CPU"':`top -b -n1 | grep "Cpu(s)" | awk '{print $2 + $4}'`})
FREE_DATA=`free -m | grep Mem` 
CURRENT=`echo $FREE_DATA | cut -f3 -d' '`
FREE=`echo $FREE_DATA | cut -f4 -d' '`
TOTAL=`echo $FREE_DATA | cut -f2 -d' '`
ramResult=$(free -m | grep "buffers/cache" | awk '{printf("{\"total\":%s,\"free\":%s}\n", $3+$4, $4)}')
#echo "{\"total\":$TOTAL,\"free\":$FREE}"
echo "$ramResult"
#echo {'"RAM"':$(echo "scale = 2; $CURRENT/$TOTAL*100" | bc)}
}

function getCpu()
{
 
cpuResult=$(echo `top -b -n1 | grep "Cpu(s)" | awk '{print $2 + $4}'`)
FREE_DATA=`free -m | grep Mem` 
CURRENT=`echo $FREE_DATA | cut -f3 -d' '`
TOTAL=`echo $FREE_DATA | cut -f2 -d' '`
#ramResult=$(free -m | grep "buffers/cache" | awk '{printf("{\"ram\":{\"total\":%s,\"free\":%s}}\n", $3, $4)}')
echo "$cpuResult"
#echo {'"RAM"':$(echo "scale = 2; $CURRENT/$TOTAL*100" | bc)}
}
function checkAllServices()
{
IFS=, read -r -a arr <<<$(cat test.csv)	

IFS=: read -r -a ipPortArr <<<${arr[0]}

if [[ ${#ipPortArr[@]} -eq 2 ]]; then
  result+="$(checkConnectivity localhost ${ipPortArr[1]})";
else
	result="$(checkService ${arr[0]})"
fi
for i in "${arr[@]:1}"; do 
IFS=: read -r -a ipPortArr <<<$i
if [[ ${#ipPortArr[@]} -eq 2 ]]; then
	result+=",$(checkConnectivity localhost ${ipPortArr[1]})";
else 
	result+=",$(checkService $i)";
fi 

done

echo "[$result]"
}

#services=$(checkAllServices)
#echo "$services"
ramResult=$(getRam)
cpuResult=$(getCpu)
diskSpace=$(getDiskSpace)
availDiskSpace
while [ $freq == "TRUE" ]
do
   echo "Disk Space low - Check diskspace on $hostname"
    availDiskSpace
    freq=FALSE
    sleep 15m
done
    
content="{\"server\":\"$(hostname)\",\"status\":\"connected\",\"cpu\":$cpuResult,\"ram\":$ramResult,\"fileSystem\":$diskSpace}"
echo "$content"
curl -D- -X POST -d "$content"  -H "Content-Type: application/json"  http://10.33.20.14:8055/api/dr/info
#curl -D- -X POST -d $diskSpace  -H "Content-Type: application/json"  http://10.195.48.112:8055/api/server/info


