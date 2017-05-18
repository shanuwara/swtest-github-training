#!python2.7

import sys, os, fnmatch
import mock, unittest
from mock import MagicMock, patch
from StringIO import StringIO


from DesignTimeParser import DesignTimeParser

class DesignTimeParserTest(unittest.TestCase):




	def setUp(self):
		self.designTime = DesignTimeParser(source=".designtime", target="file.properties", folder="/app/jenkins-slave/workspace/EIS_DevOps_buildear/dtl", debug=True)

		self.__INPUT = """#Design time libraries
						#Format: #=File Alias=Description
						#Thu Nov 03 12:33:39 IST 2016
						9=IMSCustAccountRegWrapper_MARS.projlib\=
						8=IMSCustomerAccountWrapper_MARS.projlib\=
						7=IMSPromotionWrapperLibrary_MARS.projlib\=
						6=IMSCustomerWalletWrapperProjLib_MARS.projlib\=
						5=OXIAccountWrapper20_MARS.projlib\=
						4=OXIAccountWrapper10_MARS.projlib\=
						3=OXICALLAPI_MARS.projlib\=
						2=IMSCALLAPI_MARS.projlib\=
						11=IMSPaymentMethodWrapper_MARS.projlib\=
						1=ProjectLibrary_MARS.projlib\=
						10=IMSLoyaltyWrapperLibrary_MARS.projlib\=
						0=ServiceLibrary_MARS.projlib\="""

		self.__DIR_LIST = [('/app/jenkins-slave/workspace/EIS_DevOps_buildear/dtl', ['TechnicalPrivateSchemaLibrary', 'SchemaLibraries', 'ProjectLibrary'], []),
							('/app/jenkins-slave/workspace/EIS_DevOps_buildear/dtl/TechnicalPrivateSchemaLibrary', [], ['TechnicalPrivateSchemaLibrary.projlib']),
							('/app/jenkins-slave/workspace/EIS_DevOps_buildear/dtl/SchemaLibraries', [], ['ProjectLibrary_MARS.projlib', 'ServiceLibrary_MARS.projlib']),
							('/app/jenkins-slave/workspace/EIS_DevOps_buildear/dtl/ProjectLibrary', [], ['CorrelationDataLibrary.projlib', 'OXITransactionWrapper13_MARS.projlib', 'IMSPromotionWrapperLibrary_MARS.projlib', 'BS2000Wrapper10_MARS.projlib', 'IMSCustomerWalletWrapperProjLib_MARS.projlib', 'BS2000Wrapper_MARS.projlib', 'OXISessionWrapper_MARS.projlib', 'IMSCustAccountRegWrapper_MARS.projlib', 'HierarchyLookupProjectLibrary_MARS.projlib', 'IMSPaymentMethodWrapper_MARS.projlib', 'IMSCALLAPI_MARS.projlib', 'OXIOpenBetCashOut_MARS.projlib', 'ProjectLibrary_MARS.projlib', 'CouchbaseContentReader20_MARS.projlib', 'OXIBetWrapper20_MARS.projlib', 'GBEWrapper_MARS.projlib', 'IMSCustAccountLoginWrapper_MARS.projlib', 'OXIAccountWrapper10_MARS.projlib', 'IMSCustomerAccountWrapper_MARS.projlib', 'OXIBetWrapper13_MARS.projlib', 'OXIAccountWrapper20_MARS.projlib', 'OXICALLAPI_MARS.projlib', 'ServiceLibrary_MARS.projlib', 'IMSLoyaltyWrapperLibrary_MARS.projlib', 'IMSBetWrapper_MARS.projlib', 'OXIVideoFeedWrapper11_MARS.projlib', 'OXIAccountLoginWrapper_MARS.projlib', 'OXITransactionLibrary_MARS.projlib', 'IMSPaymentWrapper_MARS.projlib'])
							]

	def test_parse(self):
		mock_open = mock.mock_open(read_data=self.__INPUT)


		with patch("__builtin__.open", mock_open) as mock_file:
			# os.path.exists = MagicMock(return_value=True)
			# assert open("path/to/open").read() == "data"

			output = self.designTime.parse()
			mock_file.assert_called_with(".designtime", "r")
			assert "IMSPromotionWrapperLibrary_MARS.projlib" in ";".join(output)

		mock_open = mock.mock_open(read_data="")
		with patch("__builtin__.open", mock_open) as mock_file:
			output = self.designTime.parse()
			print "test_parse", output

	def test_getList(self):
		

		mockWalk = MagicMock(return_value=self.__DIR_LIST)
		# mockWalk.__iter__ = lambda _: iter(self.__DIR_LIST)
		os.walk = mockWalk

		libraries = self.designTime.getList()
		self.assertIsNotNone(libraries)
		self.assertEquals("/app/jenkins-slave/workspace/EIS_DevOps_buildear/dtl/TechnicalPrivateSchemaLibrary/TechnicalPrivateSchemaLibrary.projlib", libraries["TechnicalPrivateSchemaLibrary.projlib"])
		

	def test_generateConfiguration(self):
		self.designTime.parse = MagicMock(return_value=['aaa', 'bbb'])
		mock_open = mock.mock_open()
		with patch("__builtin__.open", mock_open, create=True) as mock_file:
			self.designTime.generateConfiguration()
			mock_file.assert_called_with("file.properties", "w")






if __name__ == "__main__":
	unittest.main()