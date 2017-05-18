module MCollective
  module Agent
    class Deploy_png<RPC::Agent
      #actions
      action "webserver" do
      out = ""
      err = ""
      #cmd = "/bin/tar -xzvf #{request[:source]} -C #{request[:target]} && echo \"deploy_ver: #{request[:tag]}\" > /etc/facter/facts.d/deploy_ver.yaml"
      cmd = "python /usr/libexec/mcollective/mcollective/agent/manage_webserver.py #{request[:switch]}"
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

      action "artifactory" do
      out = ""
      err = ""
      #cmd = "/bin/tar -xzvf #{request[:source]} -C #{request[:target]} && echo \"deploy_ver: #{request[:tag]}\" > /etc/facter/facts.d/deploy_ver.yaml"
      cmd = "python /usr/libexec/mcollective/mcollective/agent/manage_artifactory.py #{request[:source]} #{request[:target]} #{request[:environment]} #{request[:service]}"
      #status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
      status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
      # if status.to_i != 0
      #   status="Failed"
      # else
      #   status="Successful"
      # end
      ###reply[:status]=status
      reply[:out]="#{out}"
      #reply[:status]=status
      ###reply[:err]=err
      end

      action "lbr" do
      out = ""
      err = ""
      #cmd = "/bin/tar -xzvf #{request[:source]} -C #{request[:target]} && echo \"deploy_ver: #{request[:tag]}\" > /etc/facter/facts.d/deploy_ver.yaml"
      cmd = "python /usr/libexec/mcollective/mcollective/agent/manage_pear.py #{request[:source]}"
      #status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
      status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
      # if status.to_i != 0
      #   status="Failed"
      # else
      #   status="Successful"
      # end
      ###reply[:status]=status
      reply[:out]="#{out}"
      #reply[:status]=status
      ###reply[:err]=err
      end

    end #class
  end   #agent
end     #module


