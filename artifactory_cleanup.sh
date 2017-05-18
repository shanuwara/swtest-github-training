function artifact_cleanup () {
base_url=$1
component=$2
number_to_keep=$3
username=$4
password=$5

api_base_url=$base_url/api/storage

curl -X GET  $api_base_url/$component > temp.json
cat temp.json  | grep uri | cut -d'"' -f4 |  grep -v http > artifact_list.txt
number_artifacts=`cat artifact_list.txt  | wc -l`

max_line=$(($number_artifacts-$number_to_keep))
i=1
for line in `cat artifact_list.txt`;
do
current_line=$(($i+1))
if [ $current_line -lt $max_line ]; then
curl -u $username:$password -X DELETE $base_url/$component$line
i=$(($i+1))
fi
done
}

artifact_cleanup "http://10.33.20.7:8080/artifactory"  "EIS/Deploy" 5 admin K_29^ob
#artifact_cleanup "http://10.33.20.7:8080/artifactory"  "eCommerce/Hybris/Release_40" 5
