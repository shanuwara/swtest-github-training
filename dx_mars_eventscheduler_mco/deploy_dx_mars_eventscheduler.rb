module MCollective
  module Agent
    class DeployPNG < RPC::Agent
      #actions
      action "deploy" do
      out = ""
      err = ""
  
      cmd = "python /usr/libexec/mcollective/mcollective/agent/dx_mars_eventscheduler/mc_deploy_eventschedulerRunner.py #{request[:url]} #{request[:package]} #{request[:target]}"
      status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
      reply[:out]="#{out}"
      reply[:err]="#{err}"
      reply.fail "an error occured #{err} " unless err.length==0
      end



    end #class
  end   #agent
end     #module
