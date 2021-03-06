param($productGUID)

if (! ( test-path -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer ))
{
  New-Item -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
  
  #New-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer -Name "SecureRepairPolicy" -Value 0 -PropertyType "DWord"
}
if (! ( test-path -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\SecureRepairWhitelist ))
{
   New-Item -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\SecureRepairWhitelist
}
$regKey=Get-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
if ($regKey.SecureRepairPolicy -eq $null)
{
   New-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer -Name "SecureRepairPolicy" -Value 2 -PropertyType "DWord"
}
$productId=$productGUID
$regKey=Get-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\SecureRepairWhitelist
if ($regKey.$productId -eq $null)
  {
    New-ItemProperty -Path Registry::HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\SecureRepairWhitelist -Name  $productId
  }  
