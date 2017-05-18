param(
   $Server,
   $UserName,
   $Password,
   $QueueName,
   [bool]$IsTransactional,
   $groups,
   $Mode='Create'   #Create or Delete
)

    $userGroups=$groups.replace("'","").split('|')
    $Pass = convertto-securestring $Password -asplaintext -force
    $UserCredentials = new-object -typename System.Management.Automation.PSCredential -argumentlist $UserName,$Pass 
      
    Invoke-Command -ComputerName $Server -ScriptBlock {                                                 
	param($QueueName,$Mode,$IsTransactional,$userGroups)
    [Reflection.Assembly]::LoadWithPartialName("System.Messaging")
	$proposedQueueName=".\private$\$QueueName"
	Write-Host $proposedQueueName
	if ($Mode -eq "Delete")
	{
	   if ([System.Messaging.MessageQueue]::Exists($proposedQueueName))
	   {
              Write-Host "Deleting queue $proposedQueueName"
             [System.Messaging.MessageQueue]::Delete($proposedQueueName)
	   }
       else
       {
              Write-Host "Queue $proposedQueueName doesn't exist for deleting"
        }
	}
	elseif($Mode -eq "Create")
	{
	   if (!([System.Messaging.MessageQueue]::Exists($proposedQueueName)))
	   {
          Write-Host "Creating queue $proposedQueueName"
		  $messageQueue = [System.Messaging.MessageQueue]::Create($proposedQueueName, $IsTransactional);
          foreach ($u in $userGroups)
		   {
             $messageQueue.SetPermissions($u, "FullControl","Allow");
           }
	   }
	}
	else
	{
	   write-error "Not accepted mode"
       Exit 1
	}


  } -Credential $UserCredentials -ArgumentList $QueueName,$Mode,$IsTransactional,$userGroups
  

if (!($?))
{
  exit 1
}
                     
     
          