#Sample run
#script  password sourceDirectory  destinationDirectory
read -r -a arr <<<$(cat servers.txt)
for i in "${arr[@]}"; do 
if [[ "$i" != '' ]]; then
        echo $i
        sshpass -p "$1"  scp -r   "$2"   rmanouche@"$i":/tmp/cqm_dr
        sshpass -p "$1"  ssh   rmanouche@"$i"  -o StrictHostKeyChecking=no -t  "echo '$1' | sudo -S  cp /tmp/cqm_dr -r -f '$3'"
		sshpass -p "$1"  ssh   rmanouche@"$i"  -o StrictHostKeyChecking=no -t  "echo '$1' | sudo -S  chmod +x '$3'/drCrobJob.sh"
		sshpass -p "$1"  ssh   rmanouche@"$i"  -o StrictHostKeyChecking=no -t  "echo '$1' | sudo -S  '$3'/drCrobJob.sh"
fi 

done