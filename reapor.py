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
LOG_FILENAME = 'the_creator.log'
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

CONST_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"

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
			# remove appropriate candidates
			log.info('deleting ' + dkey)
			bashCommand = "delete.bat " + dkey
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
			output = process.communicate()[0]
			# way to interigate response for failure?
			r.delete(dkey)
except:
	e = sys.exc_info()
	log.error(e)
