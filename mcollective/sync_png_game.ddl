metadata :name        => 'sync_png_game',
         :description => 'Syncing games for PnG',
         :author      => 'Reza.Manouchehri',
         :license     => 'Ladbrokes',
         :version     => '1.0',
         :url         => 'http://ladbrokes.com',
         :timeout     => 120

action 'sync', :description => 'Download and manage creation of games for PnG' do
    display :always

	input :userName,
          :prompt      => 'artifactory username',
          :description => 'artifactory user name',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024

  input :password,
          :prompt      => 'passowrd',
          :description => 'artifactory password',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024

    input :game,
          :prompt      => 'Game',
          :description => 'Game name',
          :type        => :string,
          :validation  => '.*',
          :optional    => false,
          :maxlength   => 1024

    input :destination,
	       :prompt   =>'Destination',
	       :description => 'Destination folder',
            :type        => :string,
            :validation  => '.*',
            :optional    => false,
            :maxlength   => 1024	

    output :output,
        :description => 'message',
        :display_as  => 'Message',
        :default     => ''
end