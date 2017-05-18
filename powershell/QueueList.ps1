Begin{
[Reflection.Assembly]::LoadWithPartialName("System.Messaging")
}
Process{
$qList= [System.Messaging.MessageQueue]::GetPrivateQueuesByMachine(".")
foreach($item in $qList){
 $queue=new-object PSObject -Property @{Name= $item.QueueName} 
 $queue 
 }
 }
 End{}