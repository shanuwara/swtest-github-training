#!python2.7 -u

# @file_version #12

import sys
import subprocess as sb
import shlex
import os
import threading

def getFile(source, target):
	print "### getFile ###"
	# cmd = "wget -P {0} {1}".format(target, source)
#	cmd = "svn export {0} {1}".format(source, target)
	# os.chdir(target)
	fileName = os.path.join(target, source.split("/")[-1])
	cmd = "curl -sS -o {0} {1}".format(fileName, source)

	parentTarget = "/".join(target.split("/")[:-1])
	if not os.path.exists(parentTarget):
		print "[ERROR] target: {0} does not exists".format(parentTarget)
		return -1


	print "[INFO] Downloading file: ", source
	print "[INFO] Executing ", cmd

	kill_proc = lambda p: p.kill()
	sb_1 = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	# timer = threading.Timer(20, kill_proc, [sb_1])
	output = ""
	try:
		# timer.start()
		(output1, output2) = sb_1.communicate()
		if output1 is not None and output1 != "":
		  output += output1

		if output2 is not None and output2 != "":
		  output += " " + output2
			
	finally:
		print output
		return fileName
		# timer.cancel()
		# if len(output) == 0:
		# 	msg = "[ERROR] Cannot download", source
		# 	raise Exception(" ".join(msg))
		# else:
		# 	print output
		# 	return fileName
	
def extractFile(source, target):
	print "### extractFile ###"
	os.chdir(target)
	os.system("ls -lah")
	cmd = "tar zxf {0} --strip-components 1".format(source)
	print "[INFO] Executing ", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	output = " ".join(proc.communicate())
	proc.wait()
	tmp = output.lower()

	if tmp.find("error") != -1 or tmp.find("denied") != -1 or tmp.find("no such file") != -1 or tmp.find("fail") != -1 or tmp.find("cannot") != -1:
		raise Exception("extractFile failure", output)

	print "Output: ", output


def chown(target):
	print "### chown ###"
	cmd = "chown content:apache -R {0}".format(target)
	print "[INFO] Executing ", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	output = " ".join(proc.communicate())
	tmp = output.lower()

	if tmp.find("error") != -1 or tmp.find("denied") != -1 or tmp.find("no such file") != -1 or tmp.find("fail") != -1:
		raise Exception("chown failure", output)

	print "Output: ", output

	cmd = "chown content:apache -R {0}../private/".format(target)
	print "[INFO] Executing ", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	output = " ".join(proc.communicate())
	tmp = output.lower()

	if tmp.find("error") != -1 or tmp.find("denied") != -1 or tmp.find("no such file") != -1 or tmp.find("fail") != -1:
		raise Exception("chown failure", output)

	print "Output: ", output



def cleanUp(target):
	print "### cleanUp ###"
	cmd = "find {0} ! -name 'static.txt' ! -path {0} -delete".format(target)
	print "[INFO] Executing ", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	output = " ".join(proc.communicate())
	print "Output: ", output

def setupConfig(target, environment, service):
	print "### setupConfig ###"

	if not target.endswith("/"):
		target += "/"

	cmd = "cp {0}_private/conf/{1}_{2}.php.config {0}../private/{2}.php.config".format(target, environment, service)
	print "[INFO] Executing ", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	output = " ".join(proc.communicate())
	tmp = output.lower()


	if tmp.find("error") != -1 or tmp.find("denied") != -1 or tmp.find("no such file") != -1 or tmp.find("fail") != -1:
		print "[ERROR] setupConfig failure", output
		raise Exception("setupConfig failure", output)

	print "Output: ", output


	cmd = "rm -rf {0}_private".format(target)
	print "[INFO] Executing ", cmd
	os.system(cmd)


def clearCache(target):
	print "### clearCache ###"
	
	cmd = "find {0} ! -path {0} -delete".format(os.path.join(target, "../logs/application/runtime/views"))
	print "[INFO] Executing ", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	output = proc.communicate()
	print output

	returnCode = proc.returncode

	cmd = "find {0} ! -path {0} -delete".format(os.path.join(target, "../logs/application/framework"))
	print "[INFO] Executing ", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	output = proc.communicate()
	print output

	return bool(proc.returncode) and bool(returnCode)


if __name__ == "__main__":
	print sys.argv
	if len(sys.argv) == 5:
		
		if sys.argv[1] != "" and sys.argv[2] != "" and sys.argv[3] != "" and sys.argv[4] != "":

			source = sys.argv[1]
			target = sys.argv[2]
			environment = sys.argv[3]
			service = sys.argv[4]

			cleanUp(target)
			fileName = getFile(source=source, target=target)
			extractFile(os.path.basename(source), target)
			setupConfig(target, environment, service)
			# chown(target)
			if fileName is not None and fileName != target:
				os.system("rm -f {0}".format(fileName))

			clearCache(target)


			print "### SUCCESS ###"
			sys.exit(0)




