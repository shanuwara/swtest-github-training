param($productGUID)

if (test-path -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer )
{
 
  if ( test-path -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\SecureRepairWhitelist )
  {
     
     $productId=$productGUID
     $regKey=Get-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\SecureRepairWhitelist
     if ($regKey.$productId -ne $null)
     {
        Remove-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\SecureRepairWhitelist -Name  $productId
     } 
     $regKey=Get-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
     if ($regKey.SecureRepairPolicy -ne $null)
      {
        Remove-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer -Name "SecureRepairPolicy" 
      } 

  }
  
}
