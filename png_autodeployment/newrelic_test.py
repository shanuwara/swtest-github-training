#!python2.7 -u

import unittest, sys, os
from StringIO import StringIO

from mock import patch, MagicMock, Mock
import mock
import newrelic


class DeploymentCase(unittest.TestCase):


	@mock.patch('newrelic.post')
	@mock.patch('settings.sb')
	def test_main_correct_config(self, mock_sb, mock_post):
		newrelic.SERVICE = "TheGrid"
		newrelic.ENVIRONMENT = "DEV"
		newrelic.REPORTER = "CQMTEST"
		newrelic.RC = "RC1"
		newrelic.JIRAKEY = "PNG-1"
		newrelic.WORKSPACE = os.getcwd()
		newrelic.PROXY = "squid01.ladbrokes.co.uk"
		newrelic.PROXY_PORT = 8080
		newrelic.APIKEY = "apikey123abc"

		mock_sb.Popen.return_value.returncode = 0
		mock_sb.Popen.return_value.communicate.return_value = (("""ServiceName,SVNName,DEV_NEWRELIC_ID,DEV_PATH,DEV_CMS_PATH,TEST_PATH,TEST_CMS_PATH,,STAGE_PATH,STAGE_CMS_PATH,PROD_DR_PATH,PROD_PATH,PROD_DR_CMS_PATH,PROD_CMS_PATH,VRA_PATH
MobileLobby,mobile,0,/var/www/vhosts/tst1-mobile.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-mobile.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-mobile.ladbrokes.com/htdocs/,,/var/www/vhosts/mobile.ladbrokes.com/htdocs/,/var/www/vhosts/mobile.ladbrokes.com/htdocs/,,,
TheGrid,mobile,42550252,/var/www/vhosts/tst1-thegrid.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-thegrid.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-thegrid.ladbrokes.com/htdocs/,,/var/www/vhosts/thegrid.ladbrokes.com/htdocs/,/var/www/vhosts/thegrid.ladbrokes.com/htdocs/,,,
Games,games,0,/var/www/vhosts/tst1-games.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-games.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-games.ladbrokes.com/htdocs/,,/var/www/vhosts/games.ladbrokes.com/htdocs/,/var/www/vhosts/games.ladbrokes.com/htdocs/,,,
Lottos,lottos,0,/var/www/vhosts/tst1-lottos.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-lottos.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-lottos.ladbrokes.com/htdocs/,,/var/www/vhosts/lottos.ladbrokes.com/htdocs/,/var/www/vhosts/lottos.ladbrokes.com/htdocs/,,,/var/www/vhosts/tst2-lottos.ladbrokes.com/htdocs/
Mobilebetting,mobilebetting,0,/var/www/vhosts/tst1-mobilebetting.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-mobilebetting.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-mobilebetting.ladbrokes.com/htdocs/,,/var/www/vhosts/mobilebetting.ladbrokes.com/htdocs/,/var/www/vhosts/mobilebetting.ladbrokes.com/htdocs/,,,
Scripts,scripts,0,/var/www/vhosts/tst1-scripts.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-scripts.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-scripts.ladbrokes.com/htdocs/,,/var/www/vhosts/scripts.ladbrokes.com/htdocs/,/var/www/vhosts/scripts.ladbrokes.com/htdocs/,,,
Common,common,0,/var/www/vhosts/tst1-common.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-common.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-common.ladbrokes.com/htdocs/,,/var/www/vhosts/common.ladbrokes.com/htdocs/,/var/www/vhosts/common.ladbrokes.com/htdocs/,,,
Home5,www,0,/var/www/vhosts/tst1-www.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-www.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-www.ladbrokes.com/htdocs/,,/var/www/vhosts/www.ladbrokes.com/htdocs/,/var/www/vhosts/www.ladbrokes.com/htdocs/,,,
FairGaming,fbg,0,/var/www/vhosts/tst1-fbg.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-fbg.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-fbg.ladbrokes.com/htdocs/,,/var/www/vhosts/fbg.ladbrokes.com/htdocs/,/var/www/vhosts/fbg.ladbrokes.com/htdocs/,,,
Exchange,ex,0,/var/www/vhosts/tst1-ex.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-ex.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-ex.ladbrokes.com/htdocs/,,/var/www/vhosts/ex.ladbrokes.com/htdocs/,/var/www/vhosts/ex.ladbrokes.com/htdocs/,,,
RetailWifi,retailwifi,0,/var/www/vhosts/tst1-retailwifi.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-retailwifi.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-retailwifi.ladbrokes.com/htdocs/,,/var/www/vhosts/retailwifi.ladbrokes.com/htdocs/,/var/www/vhosts/retailwifi.ladbrokes.com/htdocs/,,,
ResponsibleGambling,responsiblegambling,0,/var/www/vhosts/tst1-responsiblegambling.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-responsiblegambling.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-responsiblegambling.ladbrokes.com/htdocs/,,/var/www/vhosts/responsiblegambling.ladbrokes.com/htdocs/,/var/www/vhosts/responsiblegambling.ladbrokes.com/htdocs/,,,
CMS,CMSicms,0,,/var/www/vhosts/tst1-cms.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-cms.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-cms.ladbrokes.com/htdocs/,,,/var/www/vhosts/cms.ladbrokes.com/htdocs/,/var/www/vhosts/cms.ladbrokes.com/htdocs/,
MobileCMS,CMSmobile,0,,/var/www/vhosts/tst1-mobilecms.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-mobilecms.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-mobilecms.ladbrokes.com/htdocs/,,,/var/www/vhosts/mobilecms.ladbrokes.com/htdocs/,/var/www/vhosts/mobilecms.ladbrokes.com/htdocs/,
GamesCMS,CMSgames,0,,/var/www/vhosts/tst1-gamescmsadmin.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-gamescmsadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-gamescmsadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/gamescmsadmin.ladbrokes.com/htdocs/,/var/www/vhosts/gamescmsadmin.ladbrokes.com/htdocs/,
LottosCMS,CMSlottos,0,,/var/www/vhosts/tst1-lottoscmsadmin.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-lottoscmsadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-lottoscmsadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/lottoscmsadmin.ladbrokes.com/htdocs/,/var/www/vhosts/lottoscmsadmin.ladbrokes.com/htdocs/,
FairgamingCMS,CMSfairgaming,0,,/var/www/vhosts/tst1-fairgamingadmin.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-fairgamingadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-fairgamingadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/fairgamingadmin.ladbrokes.com/htdocs/,/var/www/vhosts/fairgamingadmin.ladbrokes.com/htdocs/,
RGadmin,CMSrgadmin,0,,/var/www/vhosts/tst1-rgadmin.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-rgadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-rgadmin.ladbrokes.com/htdocs/,,,/var/www/vhosts/rgadmin.ladbrokes.com/htdocs/,/var/www/vhosts/rgadmin.ladbrokes.com/htdocs/,
LBRCommon,LBRCommon,0,/usr/share/pear,,/usr/share/pear,,,/usr/share/pear,,/usr/share/pear,/usr/share/pear,,,
LBRGames,LBRGames,0,/usr/share/pear,,/usr/share/pear,,,/usr/share/pear,,/usr/share/pear,/usr/share/pear,,,
LBRUtils,LBRUtils,0,/usr/share/pear,,/usr/share/pear,,,/usr/share/pear,,/usr/share/pear,/usr/share/pear,,,
LBRGaming,LBRGaming,0,/usr/share/pear,,/usr/share/pear,,,/usr/share/pear,,/usr/share/pear,/usr/share/pear,,,
LoginAPI,loginapi,0,/var/www/vhosts/tst1-loginapi.ladbrokes.com/htdocs/,,/var/www/vhosts/tst2-loginapi.ladbrokes.com/htdocs/,,,/var/www/vhosts/stg-loginapi.ladbrokes.com/htdocs/,,/var/www/vhosts/loginapi.ladbrokes.com/htdocs/,/var/www/vhosts/loginapi.ladbrokes.com/htdocs/,,,
""", ''))


		mock_post.return_value = 201

		newrelic.main()

	@mock.patch("settings.Settings.getSettings")
	@mock.patch("newrelic.post")
	@mock.patch("newrelic.sb")
	def test_post_for_failure(self, mock_sb, mock_post, mock_getSettings):
		newrelic.SERVICE = "TheGrid"
		newrelic.ENVIRONMENT = "DEV"
		newrelic.REPORTER = "CQMTEST"
		newrelic.RC = "RC1"
		newrelic.JIRAKEY = "PNG-1"
		newrelic.WORKSPACE = os.getcwd()

		mock_getSettings.return_value = {"TheGrid": {"DEV_NEWRELIC_ID": 123}}


		mock_post.return_value = 401

		with self.assertRaises(Exception) as context:
			newrelic.main()

		self.assertItemsEqual(("Failure, status:", 401), context.exception)

	@mock.patch('settings.Settings.getSettings')
	@mock.patch('settings.sb')
	def test_main_with_incorrect_config(self, mock_sb, mock_getSettings):
		mock_getSettings.return_value = None

		with self.assertRaises(ValueError) as context:
			newrelic.main()

		self.assertTrue('Failure, incorrect config file' in context.exception)


if __name__ == "__main__":
	unittest.main()

