#
# Removes Azure resources that have met or exceeded their TTL, and audits the event
#
from datetime import datetime
import json
import redis
import logging
import logging.handlers
import sys

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('reapor')
LOG_FILENAME = 'the_creator.log'
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                               maxBytes=2000000,
                                               backupCount=50)
handler.setFormatter(formatter)
log.addHandler(handler)

log.debug("Don't fear the reapor")

try:

	r = redis.StrictRedis(host='localhost', port=6379, db=0)

	# determine which entries have met or exceeded their TTL
	for key in r.scan_iter():
		log.debug('key: ' + key.decode('utf-8'))
		log.debug('value: ' + r.get(key.decode('utf-8')).decode('utf-8'))
		obj = r.get(key.decode('utf-8')).decode('utf-8')
		jobj = json.loads(obj)
		ttl = datetime.strptime(jobj['ttl'], "%Y-%m-%d %H:%M:%S.%f")
		log.debug(ttl)
		if(ttl <= datetime.utcnow()):
			# remove appropriate candidates
			log.info('deleting ' + key.decode('utf-8'))
			#bashCommand = "delete.bat " + key
			#process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
			#output = process.communicate()[0]
			# way to interigate response for failure?
			#r.delete(key)
except:
	e = sys.exc_info()
	log.error(e)
