::Only works with usernames with no space
::Put quotes around passwotd if it contains an escaped escape characters

setlocal
set jira_id=%1
set	comment=%2
set	jirausername=%3
set Jirapwd=%4

echo {^"update^":{^"comment^":[{^"add^":{^"body^":%comment%}}]}}  > jiracomment.json
::curl -u "admin:%Jirapwd%" -X GET http://10.33.20.21:8080/jira/rest/api/2/issue/%JIRAKEY% > %JIRAKEY%.json
curl -D- -u "%jirausername%:%Jirapwd%" -X  PUT --data @jiracomment.json -H "Content-Type: application/json" http://10.33.20.21:8080/jira/rest/api/2/issue/%jira_id%