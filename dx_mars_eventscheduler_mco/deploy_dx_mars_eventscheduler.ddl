###################################################################
      metadata :name        => "deploy eventscheduler",
               :description => "deploys command",
               :author      => "Me <me@example.com>",
               :license     => "me",
               :version     => "0.1",
               :url         => "http://me.com",
               :timeout     => 300
###################################################################

action 'deploy', :description => 'deploys to tomcat' do
    display :always

    input :url,
          :prompt      => 'url',
          :description => '',
          :type        => :string,
          :validation  => '',
          :optional    => false,
          :maxlength   => 1024

    input :package,
          :prompt      => 'package',
          :description => '',
          :type        => :string,
          :validation  => '',
          :optional    => false,
          :maxlength   => 1024

    input :target,
          :prompt      => 'target',
          :description => '',
          :type        => :string,
          :validation  => '',
          :optional    => false,
          :maxlength   => 1024                    


    output :out,
        :description => 'stdout',
        :display_as  => "stdout",
        :default     => ''

    output :err,
        :description => 'stderr',
        :display_as  => "stderr",
        :default     => ''
end

