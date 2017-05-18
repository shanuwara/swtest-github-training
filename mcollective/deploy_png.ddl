###################################################################
      metadata :name        => "deploy_png",
               :description => "deploys command",
               :author      => "Me <me@example.com>",
               :license     => "me",
               :version     => "0.1",
               :url         => "http://me.com",
               :timeout     => 600
###################################################################

action 'webserver', :description => 'deploys to target dir' do
    display :always

    input :switch,
          :prompt      => 'switch',
          :description => 'start/stop',
          :type        => :string,
          :validation  => '^(start|stop|status)$',
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

    input :environment,
          :prompt      => 'environment',
          :description => 'Target environment',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024

    input :service,
          :prompt      => 'service',
          :description => 'service',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024



    output :out,
        :description => 'Your output',
        :display_as  => "Output",
        :default     => ''

end



action 'lbr', :description => 'deploys lbr' do
    display :always

    input :source,
          :prompt      => 'source',
          :description => 'url to artefactory package',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024
    output :out,
        :description => 'Your output',
        :display_as  => "Output",
        :default     => ''

end

