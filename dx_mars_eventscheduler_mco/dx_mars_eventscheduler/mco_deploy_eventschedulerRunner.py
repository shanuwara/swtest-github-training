#!python2.7 -u

from mco_deploy_eventschedulerClass import Deploy

if __name__ == "__main__":
	
	url = sys.argv[1]
	package = sys.argv[2]
	target = sys.argv[3]

	systemService = "tomcat7"

	deploy = Deploy(package=package, 
			url=url, 
			systemService=systemService, 
			target=target)