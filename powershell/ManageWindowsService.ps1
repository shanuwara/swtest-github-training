param(
$serviceList,
$action
)


$serviceArray=$serviceList.replace("'","").split('|')
$foundServices=Get-Service |Where { $serviceArray -Contains  $_.Name }

if ($foundServices)
{
   if ($action -eq "start")
   {
      foreach ($s in $foundServices|Where{$_.Status -ne "running" })
      {
	    #Set-Service "$($s.Name)"   -StartupType $startupType
	    Write-Host "Starting $($s.Name)"
        $s.start()
      }
   }
   elseif ($action -eq "stop")
   {
      foreach ($s in  $foundServices|Where{$_.Status -ne "stopped" })
      {
	     Write-Host "Stopping $($s.Name)"
         $s.stop()
      }
   }
   else
   {
     Write-Error "The action $action is not valid "
     throw [System.Exception] "The action $action is not valid "
   }
}