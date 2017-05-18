module MCollective
  module Agent
    class Sync_png_game<RPC::Agent
      action "sync" do
	out=""
	err=""
    #reply[:output] = request[:msg]
	cmd = "python /usr/libexec/mcollective/mcollective/agent/pngGame.py #{request[:userName]} #{request[:password]} #{request[:game]} #{request[:destination]}"
    status = run("#{cmd}", :stdout => out, :stderr => err, :chomp => true)
	reply[:out]="#{out}"
	reply[:output]="#{err}"
	reply.fail "an error occured #{err} " unless err.length==0
      end
    end
  end
end
