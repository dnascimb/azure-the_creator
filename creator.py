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
log = logging.getLogger('creator')
LOG_FILENAME = 'creator.log'
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
	reapor_data = {
		'resource_group_name' : randName,
   		'created_at' : ''+datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
   		'ttl' : ''+(datetime.utcnow() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	}

	#create resources and save audit to redis
	try:
		#generate random names for everything
		param_file = open('azuredeploy.parameters.json', "r")    
		data = json.load(param_file)
		randName_condensed = randName.replace("-", "")
		randName_condensed = randName_condensed[:12]
		data["publicDnsName1"]["value"] = "kvm1-" + randName
		data["publicDnsName2"]["value"] = "kvm2-" + randName
		data["publicDnsName3"]["value"] = "kvm3-" + randName
		data["vmName1"]["value"] = "vm1" + randName_condensed
		data["vmName2"]["value"] = "vm2" + randName_condensed
		data["vmName3"]["value"] = "vm3" + randName_condensed
		output_filename = randName + "-parameters.json"
		param_out = open(output_filename,"w")
		param_out.write(json.dumps(data))
		param_out.close()

		bashCommand = "create.bat " + randName + " " + output_filename


		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
		output = process.communicate()[0]
		str_output = output.decode('UTF-8')
		log.info("result of running azure cli:" + str_output)
		if('Succeeded' in str_output):
			r = redis.StrictRedis(host='localhost', port=6379, db=0)
			r.set(randName, json.dumps(reapor_data))
			log.info("created resource " + str(r.get(randName)));
		else:
			log.error("Resource Group creation did not return success")
			return json.dumps({'status':'errored'})
	except:
		e = sys.exc_info()
		log.error(e)
		return e
	
#	return str_output
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
