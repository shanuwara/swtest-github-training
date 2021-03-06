$userName='cqm'
$password='cqm'
$ServerName='lesii-trader-06'# the server it is on
$Database='Football' # the name of the database you want to script as objects
$DirectoryToSaveTo='C:\MyScriptsDirectory' # the directory where you want to store them
# Load SMO assembly, and if we're running SQL 2008 DLLs load the SMOExtended and SQLWMIManagement libraries
[System.Reflection.Assembly]::LoadWithPartialName( 'Microsoft.SqlServer.ConnectionInfo')
$v = [System.Reflection.Assembly]::LoadWithPartialName( 'Microsoft.SqlServer.SMO')
if ((($v.FullName.Split(','))[1].Split('='))[1].Split('.')[0] -ne '9') {
   [System.Reflection.Assembly]::LoadWithPartialName('Microsoft.SqlServer.SMOExtended') | out-null
}
[System.Reflection.Assembly]::LoadWithPartialName('Microsoft.SqlServer.SmoEnum') | out-null
set-psdebug -strict # catch a few extra bugs
$ErrorActionPreference = "stop"
$My='Microsoft.SqlServer.Management.Smo'
$mySrvConn = new-object ("Microsoft.SqlServer.Management.Common.ServerConnection")
$mySrvConn.ServerInstance=$ServerName
$mySrvConn.LoginSecure = $false
$mySrvConn.Login = $userName
$mySrvConn.Password = $password

$srv = new-object ("$My.Server") $mySrvConn # attach to the server
if ($srv.ServerType-eq $null) # if it managed to find a server
   {
   Write-Error "Sorry, but I couldn't find Server '$ServerName' "
   return
}
$scripter = new-object ("$My.Scripter") $srv # create the scripter
$scripter.Options.ToFileOnly = $true
$scripter.Options.ExtendedProperties= $true # yes, we want these
$scripter.Options.DRIAll= $true # and all the constraints
$scripter.Options.Indexes= $true # Yup, these would be nice
$scripter.Options.Triggers= $true # This should be includede
# first we get the bitmap of all the object types we want
$objectsToDo =[long]  [Microsoft.SqlServer.Management.Smo.DatabaseObjectTypes]::Table -bor [Microsoft.SqlServer.Management.Smo.DatabaseObjectTypes]::View -bor [Microsoft.SqlServer.Management.Smo.DatabaseObjectTypes]::StoredProcedure -bor [Microsoft.SqlServer.Management.Smo.DatabaseObjectTypes]::UserDefinedFunction -bor [Microsoft.SqlServer.Management.Smo.DatabaseObjectTypes]::UserDefinedType
# and we store them in a datatable
$d = new-object System.Data.Datatable
# get just the tables
$d=$srv.databases[$Database].EnumObjects($objectsToDo)

# and write out each scriptable object as a file in the directory you specify
$d | where { $_.Schema -ne ''}| FOREACH-OBJECT { # for every object we have in the datatable.
    $SavePath="$($DirectoryToSaveTo)\$($_.DatabaseObjectTypes)\$($_.Schema)"
    # create the directory if necessary (SMO doesn't).
    if (!( Test-Path -path $SavePath )) # create it if not existing
           {Try { New-Item $SavePath -type directory | out-null }
        Catch [system.exception]{
             Write-Error "error while creating '$SavePath' $_"
             return
             }
        }
    # tell the scripter object where to write it
    $scripter.Options.Filename = "$SavePath\$($_.name -replace '[\\\/\:\.]','-').sql";
    # Create a single element URN array
    $UrnCollection = new-object ("$My.urnCollection")
    $URNCollection.add($_.urn)
    # and write out the object to the specified file
    $scripter.script($URNCollection)
    }
"All is written out"