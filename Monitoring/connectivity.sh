#!/bin/bash

function checkService()
{
result=$(ps -ef | grep $1  | grep -v grep)
[ $?  -eq "0" ] && echo "{\"service\":\"$1\",\"status\":\"running\"}" || echo "{\"service\":\"$1\",\"status\":\"not running\"}"

}

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
