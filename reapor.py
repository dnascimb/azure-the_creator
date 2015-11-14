#
# Removes Azure resources that have met or exceeded their TTL, and audits the event
#
from datetime import datetime
import json
import redis
import logging
import logging.handlers
import sys
import subprocess

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('reapor')
LOG_FILENAME = 'the_reaper.log'
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

CONST_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"

CONST_AZURE_STORAGE_ACCOUNT = "testflightdynamicstorage"
CONST_AZURE_STORAGE_ACCOUNT_KEY = "\"kwy1i5Jl4ASk8gjrYSFJp8TcLfnghnx/uyo4qlNFab40iiBYZfS3BlDCmOLE6ql2U0rkIqkQSbiyty9Veo39Pg==\""  # must use quotes to handle the '=' characters



# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                               maxBytes=2000000,
                                               backupCount=50)
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Don't fear the reapor")
# ensure that the azure system is running in arm mode
# this command takes 1.5 seconds to run and could be executed before every azure call is issues arise with other processes that set the mode to asm
subprocess.Popen('azure config mode arm', shell=True).wait()


try:
	r = redis.StrictRedis(host='localhost', port=6379, db=0)

	# determine which entries have met or exceeded their TTL
	for key in r.scan_iter():
		dkey = key.decode('utf-8')
		log.debug('key: ' + dkey)
		log.debug('value: ' + r.get(dkey).decode('utf-8'))
		obj = r.get(dkey).decode('utf-8')
		jobj = json.loads(obj)
		ttl = datetime.strptime(jobj['ttl'], CONST_TIME_FMT)
		
		if(ttl <= datetime.utcnow()):
#		if(True):
			# remove appropriate candidates
			log.info('deleting ' + dkey)
			bashCommand = "delete.bat " + dkey
			# the "delete group" command blocks, and it can take up to 10 minutes for this command to return
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd="c:/github/azure-the_creator/")  
			output = process.communicate()[0]
			# way to interigate response for failure?
			str_output = output.decode('UTF-8')
			log.info("result of running azure delete command:" + str_output)
			
			# clean up extra crap that doesn't get deleted
			# Underlying blobs (VHDs and status files) are not deleted by default when you delete virtual machines

			randName_condensed = dkey.replace("-", "")
			randName_condensed = randName_condensed[:12]
			for vmprefix in ["vm1", "vm2", "vm3"]:
				bashCommand = "list_underlying_blobs.bat " + vmprefix + randName_condensed + " " + CONST_AZURE_STORAGE_ACCOUNT + " " + CONST_AZURE_STORAGE_ACCOUNT_KEY
				# use shell=true and a command string to preserve == characters at end of the account key
				process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True, cwd="c:/github/azure-the_creator/")  
				output = process.communicate()[0]
				str_output = output.decode("UTF-8")
				# log.info("result of running azure list command:" + str_output)

				json_data = json.loads(str_output)
				for blob in json_data:
					blob_name = blob["name"]
					log.info("deleting underlying blob: [" + blob_name + "]")
					bashCommand = "delete_underlying_blob.bat " + blob_name + " " + CONST_AZURE_STORAGE_ACCOUNT + " " + CONST_AZURE_STORAGE_ACCOUNT_KEY
					# use shell=true and a command string to preserve == characters at end of the account key
					process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True, cwd="c:/github/azure-the_creator/")  
					output = process.communicate()[0]

			r.delete(dkey)
except:
	e = sys.exc_info()
	log.error(e)
