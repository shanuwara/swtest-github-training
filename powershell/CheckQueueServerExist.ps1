param(
   $Server,
   $UserName,
   $Password
)

   #$serviceList=dism /online /get-features /format:table 
   #$msmqList=$serviceList | Where-Object { $_ -like 'msmq*' -and $_ -like '*disabled*'  }
   #foreach($Item in $msmqList) {  $feature=$item.trim().split(' ',[System.StringSplitOptions]::RemoveEmptyEntries)[0];  dism /online /enable-feature  /featurename:$feature  /all /NoRestart}

   $Pass = convertto-securestring $Password -asplaintext -force
   $UserCredentials = new-object -typename System.Management.Automation.PSCredential -argumentlist $UserName,$Pass 
   Invoke-Command -ComputerName $Server -ScriptBlock {                                                 
       $serviceList=dism /online /get-features /format:table
       $msmqList=$serviceList | Where-Object { $_ -like 'msmq*' -and $_ -like '*disabled*'  } 
       foreach($Item in $msmqList) {  $feature=$item.trim().split(' ',[System.StringSplitOptions]::RemoveEmptyEntries)[0];  dism /online /enable-feature  /featurename:$feature  /all /NoRestart}

       $serviceList=dism /online /get-features /format:table
       $msmqResult=$serviceList | Where-Object { $_ -like 'MSMQ-Server' -and $_ -like '*disabled*'  }
       if($msmqResult -ne $NULL)
       {
          write-error "Queue Server is not installed"
          Exit 1
        } 	

     } -Credential $UserCredentials 

if (!($?))
{
  exit 1
}