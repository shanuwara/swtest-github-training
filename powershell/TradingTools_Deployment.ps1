param(
   $UserName,
   $Password,
   $RC , # Will be passed by Jenkins
  $MSIFile  = "",
  $Servers='' ,# for multi servser use comma separated ,
  $PackageName=''
)

$ScriptExitCode = 0

try
{
  
    $ErrorActionPreference = "Stop" # Set this to stop script execution in event of any error. TODO - keeping things simple for now and the script can be made more complex to add recovery and rollback routines
    	
    # NOTE : Set servers in the environment..add more server nodes comma separated as needed
     $sharedFolderName="TradingToolsDeployments"

   

    # NOTE - Change the credentials with user having Admin rights to deploy on the server
    $Pass = convertto-securestring $Password -asplaintext -force
    $UserCredentials = new-object -typename System.Management.Automation.PSCredential -argumentlist $UserName,$Pass 
 
    # Folder on the server where the timestamped folder will be created for deployment
    $ServerFolderPath = $PackageName+"\$RC" 
    $BaseServerFolderPath = $PackageName+"\" 
    # Diagnostic for the confguration used for the script in current execution

 
    Write-Host "Starting deploying "+$PackageName+" components on $Environment (Server : $Servers)"	
	

    # Iterate over each server configured in the chosen target environment
    $Servers.Split(",") | foreach { 
                      
        Write-Host "Started deployment on server node : $_"        
        $ServerName = $_   

          

        # Create new folder on the remote host
        Invoke-Command -ComputerName $ServerName -ScriptBlock {                                                 
                                                        param($BaseServerFolderPath,$ServerFolderPath,$sharedFolderName)
														$hostName=hostname
														$Shares=[WMICLASS]”WIN32_Share”
                                                     
														IF (!(TEST-PATH C:\$sharedFolderName)) 
                                                        { 
																						NEW-ITEM  C:\$sharedFolderName -type Directory 
                                                                       
										                }
														
														If (!(GET-WMIOBJECT Win32_Share -filter “name='$sharedFolderName'”)) 
                                                        { 
                                                                net share "$sharedFolderName=c:\$sharedFolderName" "/GRANT:BUILTIN\Administrators,FULL"
																		#$Shares.Create("C:\$sharedFolderName",$sharedFolderName,0) 
                                                                   
                                                                        #$acl = Get-Acl  \\$hostname\$sharedFolderName
                                                                        #$permission = "BUILTIN\Administrators","FullControl","Allow"
                                                                        #$accessRule = New-Object   System.Security.AccessControl.FileSystemAccessRule   $permission
                                                                        
                                                                       #$acl.setAccessRule($accessRule)
                                                                       #$acl |  Set-Acl \\$hostname\$sharedFolderName
                                                                         
                                                         }
                                         
                                                                    
														
														if(Test-Path -Path  \\$hostName\$sharedFolderName\$BaseServerFolderPath) # only create new folder if it does not exist already
                                                        {
                                                           #Write-Host 'Deleting old items '
														   #Get-ChildItem -Path \\$hostName\$sharedFolderName\$BaseServerFolderPath |Remove-Item -Force  -Confirm:$false -Recurse
                                                           
															     
                                                        }
                                                        if(!(Test-Path -Path  \\$hostName\$sharedFolderName\$ServerFolderPath)) # only create new folder if it does not exist already
                                                        {
                                                            Write-Host 'Creating new folder'
                                                            New-Item \\$hostName\$sharedFolderName\$ServerFolderPath -ItemType Dir          
                                                        }
                                                        Else
                                                        {
                                                           Write-Host 'Skipping folder creation'
                                                        }
														
														 Write-Host 'Keeping just two latest'
														 
														 $list=Get-ChildItem -Path \\$hostName\$sharedFolderName\$BaseServerFolderPath |Sort-Object{$_.LastWriteTime}|select Name

														if ($list -ne $NULL -and $list.length -gt 2)
														{
														  $count=$list.length-2
														   for($i=0;$i -lt $count ;$i=$i+1) 
														   {
														      $childName=$list[$i].Name
															   Remove-Item  \\$hostName\$sharedFolderName\$BaseServerFolderPath\$childName -Force -Recurse
															}
														}

                                                      } -Credential $UserCredentials -ArgumentList $BaseServerFolderPath,$ServerFolderPath,$sharedFolderName
                     
     
          

                 
                 # Copy MSI on the remote server   
                 Write-Host "MSIFile = $MSIFile"
						net use
						net use /delete * /y
						net use w: "\\$ServerName\$sharedFolderName\$PackageName\$RC" /USER:$UserName $Password
              
                         #Write-Host "$_"
						 #Write-Host $TargetFolderPath
						 Write-Host 'Try copying msi '  "$_"   
						 Write-Host $(whoami)				 
						 
						 						 
						 
						 if(!(Test-Path  $MSIFile))
						{
							Write-Error "Msi:$MsiFile  not found"
							Exit 1
						} 
					   write-host "Copying  $MsiFile"
						XCOPY $MSIFile "\\$ServerName\$sharedFolderName\$PackageName\$RC" /y
						#net use /delete * /y
						
						Write-Host 'Copied msi to remote host'
                             
				net use /delete * /y
				net use
				$fileName= Split-Path  $MSIFile -Leaf
                Invoke-Command -ComputerName $ServerName -ScriptBlock { # Remote scrip execution block
                                        param($ServerFolderPath,$fileName,$sharedFolderName)
									     $hostName=hostname
										 if(!(Test-Path  \\$hostName\$sharedFolderName\$ServerFolderPath\$fileName))
										{
											Write-Error "Msi:$fileName  not found on destination"
											Exit 1
										} 
                                        # Install new version of the component
										Write-Host "$ServerFolderPath\"
										write-host "Start installing $fileName"
										$fileNameWithoutExtenstion= [io.path]::getfilenamewithoutextension($fileName)
										#msiexec /i MarketGeneratorSetup_1.0.%BUILD_NUMBER%.%SVN_REVISION%.msi ADDLOCAL=ALL /qb  targetdir=E:\Application /lv MarketGeneratorSetup.log
                                        $p = (Start-Process -FilePath msiexec -ArgumentList " /i ""\\$hostName\$sharedFolderName\$ServerFolderPath\$fileName""   ADDLOCAL=ALL   /qn   REBOOT=ReallySuppress  MSIRESTARTMANAGERCONTROL=DisableShutdown  MSIDISABLERMRESTART=1  /norestart     targetdir=E:\Application /l*v \\$hostName\$sharedFolderName\$ServerFolderPath\$fileNameWithoutExtenstion.log " -Wait -PassThru)

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
										    
										    Write-Error "Msi:$fileName  not installed properly. $errorCode"
											Exit 1
										}
										Write-Host 'New version installed'
                                        Write-Host "Installed $ServerFolderPath\$fileName"
                                        Write-Host 'Component processing ends'
										
                                   

                            } -Credential $UserCredentials -ArgumentList $ServerFolderPath,$fileName,$sharedFolderName
                

        
  
     
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
