module MCollective
  module Agent
    class DeployPNG < RPC::Agent
      #actions
      action "webserver" do
      out = ""
      err = ""
      #cmd = "/bin/tar -xzvf #{request[:source]} -C #{request[:target]} && echo \"deploy_ver: #{request[:tag]}\" > /etc/facter/facts.d/deploy_ver.yaml"
      cmd = "python /home/mzawadzk/manage_webserver.py #{request[:switch]}"
      status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
      # if status.to_i > 0
      #   status="Failed"
      # else
      #   status="Successful"
      # end
      ###reply[:status]=status
      reply[:out]="#{out}"
      ###reply[:err]=err
      end

      action "webserver" do
      out = ""
      err = ""
      #cmd = "/bin/tar -xzvf #{request[:source]} -C #{request[:target]} && echo \"deploy_ver: #{request[:tag]}\" > /etc/facter/facts.d/deploy_ver.yaml"
      cmd = "python /home/mzawadzk/manage_artifactory.py #{request[:source]} #{request[:target]}"
      status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
      # if status.to_i > 0
      #   status="Failed"
      # else
      #   status="Successful"
      # end
      ###reply[:status]=status
      reply[:out]="#{out}"
      ###reply[:err]=err
      end


    end #class
  end   #agent
end     #module


