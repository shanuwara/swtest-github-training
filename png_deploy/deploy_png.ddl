###################################################################
      metadata :name        => "deploy png",
               :description => "deploys command",
               :author      => "Me <me@example.com>",
               :license     => "me",
               :version     => "0.1",
               :url         => "http://me.com",
               :timeout     => 60
###################################################################

action 'webserver', :description => 'deploys to target dir' do
    display :always

    input :switch,
          :prompt      => 'switch',
          :description => 'start/stop',
          :type        => :string,
          :validation  => '^(start|stop)$',
          :optional    => false,
          :maxlength   => 1024


    output :out,
        :description => 'Your output',
        :display_as  => "Output",
        :default     => ''

end


action 'artifactory', :description => 'deploys to target dir' do
    display :always

    input :source,
          :prompt      => 'source',
          :description => 'Link to repository',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024

    input :target,
          :prompt      => 'target',
          :description => 'Target folder path',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024

    output :out,
        :description => 'Your output',
        :display_as  => "Output",
        :default     => ''

end

