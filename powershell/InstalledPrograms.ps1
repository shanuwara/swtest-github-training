[cmdletbinding()]            
param(                 
         $filter=$Null  ,
		 $fileName=$Null
)            


           
                       
begin {            
 $UninstallRegKeys=@("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",            
     "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall")            
 $regUpgradeKeys=Get-ChildItem -Path Registry::HKEY_CLASSES_ROOT\Installer\UpgradeCodes
 
}            
           
process {
   $list=@()
   
function Reverse($s)
{
 if ($s -eq $null -or $s.length -eq 0)
 {
 return "";
 }
 $byteAr=$s.ToCharArray()
 [array]::Reverse($byteAr)
 return   -join($byteAr)
}

function PackGuid($guid)
{
try
{
$result=""
$stripedGuid=$guid.replace("{","")
$stripedGuid=$stripedGuid.replace("}","")
$splited=$stripedGuid -split '-' 
if($splited.length -gt 5)
{
 return "";
}
for($i=0;$i -lt 3;$i++)
{
  $result+=Reverse $splited[$i]
}
for($i=3;$i -lt 5;$i++)
{

for($j=0;$j -lt $splited[$i].length; $j+=2)
{
  $result+=Reverse $splited[$i].substring($j,2)

}
}
return $result
}
catch
{
return ""
}
}

function GetUpgradeCode($productGuid)
{
 $packedGuid=PackGuid $productGuid
  if  ($packedGuid -eq "")
 {
   return ""
 }
 $regKey=$regUpgradeKeys | where {$_.Property[$_.Property.length-1].ToUpper().contains($packedGuid.ToUpper())}
 
 if  ($regKey -eq $NULL -OR $regKey.Name -eq $Null)
 {
   return ""
 }
 $UpgradeCode=$regKey.Name.Replace('HKEY_CLASSES_ROOT\Installer\UpgradeCodes\','')
 return ([Guid]$regKey.Name.Replace('HKEY_CLASSES_ROOT\Installer\UpgradeCodes\','')).ToString("B").ToUpper()
} 

 [string[]]$ComputerName = $env:computername 
 
 foreach($Computer in $ComputerName) {            
  Write-Verbose "Working on $Computer"            
 if(Test-Connection -ComputerName $Computer -Count 1 -ea 0) {            
  foreach($UninstallRegKey in $UninstallRegKeys) {            
   try {            
    $HKLM   = [microsoft.win32.registrykey]::OpenRemoteBaseKey('LocalMachine',$computer)            
    $UninstallRef  = $HKLM.OpenSubKey($UninstallRegKey)            
    $Applications = $UninstallRef.GetSubKeyNames()            
   } catch {            
    Write-Verbose "Failed to read $UninstallRegKey"            
    Continue            
   }            
            
   foreach ($App in $Applications) {
   
     
   $AppRegistryKey  = $UninstallRegKey + "\\" + $App            
   $AppDetails   = $HKLM.OpenSubKey($AppRegistryKey)            
   $AppGUID   = $App            
   $AppDisplayName  = $($AppDetails.GetValue("DisplayName"))            
   $AppVersion   = $($AppDetails.GetValue("DisplayVersion"))            
   $AppPublisher  = $($AppDetails.GetValue("Publisher"))            
   $AppInstalledDate = $($AppDetails.GetValue("InstallDate"))
   if($AppInstalledDate)   
   {
     $AppInstalledDate=[String]::Format("{0}-{1}-{2}",$AppInstalledDate.Substring(0,4),$AppInstalledDate.Substring(4,2),$AppInstalledDate.Substring(6,2))
   }
   $AppUninstall  = $($AppDetails.GetValue("UninstallString"))            
   if($UninstallRegKey -match "Wow6432Node") {            
    $Softwarearchitecture = "x86"            
   } else {            
    $Softwarearchitecture = "x64"            
   }            
   if(!$AppDisplayName) { continue }  
   
   $upgradeGUID= GetUpgradeCode($AppGUID)          
   $OutputObj = New-Object -TypeName PSobject             
   $OutputObj | Add-Member -MemberType NoteProperty -Name ComputerName -Value $Computer.ToUpper()            
   $OutputObj | Add-Member -MemberType NoteProperty -Name AppName -Value $AppDisplayName            
   $OutputObj | Add-Member -MemberType NoteProperty -Name AppVersion -Value $AppVersion            
   $OutputObj | Add-Member -MemberType NoteProperty -Name AppVendor -Value $AppPublisher            
   $OutputObj | Add-Member -MemberType NoteProperty -Name InstalledDate -Value $AppInstalledDate            
   #$OutputObj | Add-Member -MemberType NoteProperty -Name UninstallKey -Value $AppUninstall  
   $OutputObj | Add-Member -MemberType NoteProperty -Name UpgradeGUID -Value           $upgradeGUID
   $OutputObj | Add-Member -MemberType NoteProperty -Name AppGUID -Value $AppGUID            
   $OutputObj | Add-Member -MemberType NoteProperty -Name SoftwareArchitecture -Value $Softwarearchitecture            
   if (!$filter -or  $AppDisplayName -like '*'+$filter+'*' -or $AppPublisher -like '*'+$filter+'*')   
     {
	   $list+=$OutputObj
	   $OutputObj 
	 }
   
       } 
  }             
 }            
 } 
if($fileName)
   {
     $list | Export-CSV $fileName -NoTypeInformation
   }
}            
            
end {}