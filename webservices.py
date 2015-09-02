from flask import Flask
from datetime import datetime, timedelta
import uuid
import redis
import sys
import json
import subprocess
import logging
import logging.handlers

app = Flask(__name__)

# setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('reapor')
LOG_FILENAME = 'the_creator.log'
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                               maxBytes=2000000,
                                               backupCount=50)
handler.setFormatter(formatter)
log.addHandler(handler)


#
# Quick way to test that the services are running
#
@app.route("/", methods=['GET'])
def greetings():
	return "The Creator"

#
# Generates a unique name, creates Azure resources with the name, and makes an entry in the ledger
#
@app.route("/resources", methods=['POST'])
def create():
	randName = str(uuid.uuid4()) # generate unique name for the resources
	bashCommand = "create.bat " + randName
	data = {
		'name' : randName,
   		'created_at' : ''+datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
   		'ttl' : ''+(datetime.utcnow() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	}

	#create resources and save audit to redis
	try:
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
		output = process.communicate()[0]

		r = redis.StrictRedis(host='localhost', port=6379, db=0)
		r.set(randName, json.dumps(data))
		log.info("created resource " + str(r.get(randName)));
	except:
		e = sys.exc_info()
		log.error(e)
		return e

	# hand back the details about the resource
	result = data
	
	return json.dumps(data)


#
# Terminates a specific resource group from Azure
#
@app.route("/resources/<machine>", methods=['DELETE'])
def delete(machine):
	bashCommand = "delete.bat " + machine
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
	output = process.communicate()[0]
	return output


if __name__ == "__main__":
    app.run()