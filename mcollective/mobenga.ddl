###################################################################
      metadata :name        => "mobenga",
               :description => "Get timestamp of deployed files",
               :author      => "Me <me@example.com>",
               :license     => "me",
               :version     => "1.0",
               :url         => "http://me.com",
               :timeout     => 600
###################################################################

action 'getTime', :description => 'Query target dir' do
    display :always

    input :filePath,
          :prompt      => 'FilePath',
          :description => 'Deploytime',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024


    output :returnTime,
        :description => 'The Timestamp of the deployed war file',
        :display_as  => "Time Deployed",
        :default     => ''

end
