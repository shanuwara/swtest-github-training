#version 1.0
module MCollective
  module Agent
    class Sync_png_media<RPC::Agent
      action "sync" do
	out=""
	err=""
    
	cmd = "su - content -c \"rsync  -rlzi  #{request[:sourcePath]} #{request[:serverIp]}:/#{request[:destPath]}\""
	
    status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
	reply[:outputMsg]="#{out}"
	reply[:errMsg]="#{err}"
	reply.fail "an error occured #{err} " unless err.length==0
      end
    end
  end
end