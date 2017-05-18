module MCollective
  module Agent
    class Mobenga<RPC::Agent
      #actions
      action "getTime" do
      out = ""
      err = ""
      if File.exist?(request[:filePath])
        reply[:returnTime]= File.mtime(request[:filePath]).strftime("%Y%m%d+%H:%M:%S")
      end
      # if status.to_i > 0
      #   status="Failed"
      # else
      #   status="Successful"
      # end
      ###reply[:status]=status
      #reply[:out]="#{out}"
      ###reply[:err]=err
      end

    end #class
  end   #agent
end     #module
