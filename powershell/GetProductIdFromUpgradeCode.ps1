
param(            
 
 [string]$upgradeGuid

)  

   
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


 $packedGuid=PackGuid $upgradeGuid
 $regKey=Get-ChildItem -Path Registry::HKEY_CLASSES_ROOT\Installer\UpgradeCodes | where {$_.Name.ToUpper().contains($packedGuid.ToUpper())} 

 if  ($regKey -eq $NULL  -OR $regKey.Property -eq $Null)
 {
   return ""
 }
 $prop= $regKey.Property[$regKey.Property.length-1]

 $productCode=([Guid]$prop).ToString()
 #write-host $productCode
 $productGuid= PackGuid $productCode
 return ([Guid]$productGuid).ToString()
