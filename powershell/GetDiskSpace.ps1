get-WmiObject win32_logicaldisk | Select-Object @{Name="ComputerName";Expression={ hostname }}, DeviceId,FreeSpace,Size,@{Name="FreePercentage";Expression={ "{0:N0}" -f  ($_.FreeSpace/$_.Size*100)}}