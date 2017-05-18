metadata :name        => 'sync_png_media',
         :description => 'Syncing media for PnG',
         :author      => 'Reza.Manouchehri',
         :license     => 'Ladbrokes',
         :version     => '1.0',
         :url         => 'http://ladbrokes.com',
         :timeout     => 120

action 'sync', :description => 'Download and manage creation of games for PnG' do
    display :always

	

    input :sourcePath,
	       :prompt   =>'Source path Sync',
	       :description => 'path to source folder',
            :type        => :string,
            :validation  => '.*',
            :optional    => false,
            :maxlength   => 1024	

	input :destPath,
	       :prompt   =>'destination path Sync',
	       :description => 'path to dest folder',
            :type        => :string,
            :validation  => '.*',
            :optional    => false,
            :maxlength   => 1024	
	input :serverIp,
	       :prompt   =>'server ip',
	       :description => 'ip of destination server',
            :type        => :string,
            :validation  => '.*',
            :optional    => false,
            :maxlength   => 1024	

    output :output,
        :description => 'message',
        :display_as  => 'Message',
        :default     => ''
end