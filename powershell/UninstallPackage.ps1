param(
   $UserName,
   $Password,
  $Servers,
  $ProductCode,
  $PackageName
)

$ScriptExitCode = 0

try
{
    $tempGuid=[GUID] $productCode
	$productGuid=$tempGuid.ToString("B")
    $ErrorActionPreference = "Stop" # Set this to stop script execution in event of any error. TODO - keeping things simple for now and the script can be made more complex to add recovery and rollback routines
    	
    # NOTE : Set servers in the environment..add more server nodes comma separated as needed
     $sharedFolderName="TradingToolsDeployments"

   

    # NOTE - Change the credentials with user having Admin rights to deploy on the server
    $Pass = convertto-securestring $Password -asplaintext -force
    $UserCredentials = new-object -typename System.Management.Automation.PSCredential -argumentlist $UserName,$Pass 
 


    # Iterate over each server configured in the chosen target environment
    $Servers.Split(",") | foreach { 
                      
        Write-Host "Started deployment on server node : $_"        
        $ServerName = $_   

             
         Invoke-Command -ComputerName $ServerName -ScriptBlock { # Remote scrip execution block
                                        param($ProductGuid,$PackageName)
									
									    $destFolder="C:\TradingToolsDeployments\Rollbacks\$PackageName"
										IF (!(TEST-PATH $destFolder)) 
                                           { 
												NEW-ITEM  $destFolder -type Directory 
                                                                       
										    }
														
                                        # Uninstall  
										
										$fileNameWithoutExtenstion= $ProductGuid
										
                                        $p = (Start-Process -FilePath msiexec -ArgumentList " /x ""$ProductGuid""   /q    /l*v $destFolder\$fileNameWithoutExtenstion.log " -Wait -PassThru)
                                       
                                        Write-Host 'Uninstalling started'

                                        # Wait till msiexec exits to avoid parallel installations
                                        do {
                                            Start-Sleep -Seconds 1 
                                            Write-Host "Waiting.."
                                            }                                    
                                        until ($p.HasExited)
                                        $errorCode=$p.ExitCode
                                        Write-Host "ExitCode : $errorCode" 
                                                                           
										if ($errorCode -ne 0)
										{
										   
										    Write-Error "ProductCode:$ProductGuid  uninstallation failed. $errorCode"
											Exit 1
										}
                                    
                                        Write-Host 'Component uninstallation ends'
										
                                   

                            } -Credential $UserCredentials -ArgumentList $productGuid,$PackageName
                

        
  
     
    } 

    

}
catch 
{
    $ErrorMessage = $_.Exception.Message
    Write-Host  "ERROR : $ErrorMessage"
    $ScriptExitCode = 1
}




Write-Host 'Finished'

Exit $ScriptExitCode
