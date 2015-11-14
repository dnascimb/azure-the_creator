from flask import Flask
from flask import abort
from flask import request
from datetime import datetime, timedelta
from flask.ext.cors import CORS, cross_origin
from email.utils import parseaddr

import uuid
import redis
import sys
import json
import subprocess
import logging
import logging.handlers

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/resources": {"origins": "*"}})


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

# Constants definition
JSON_TTL = "ttl"
JSON_RESOURCE_GROUP_NAME = "resource_group_name"
JSON_CREATED_AT = "created_at"
JSON_EMAIL = "email"

CONST_TIMEDELTA_TO_LIVE_MINUTES = timedelta(minutes=int(135))   # 2 hours plus 15 minutes to allow for Azure deployment
CONST_MAXTIMEDELTA_TO_LIVE_MINUTES = timedelta(minutes=int(240))

CONST_MAX_ALLOCATED_SYSTEMS = 13

CONST_AZURE_STATUS_SUCCEEDED = "Succeeded"
CONST_AZURE_STATUS_FAILED = "Failed"
CONST_AZURE_STATUS_CREATING = "Running"
CONST_AZURE_PROVISIONING_STATE = "ProvisioningState"

CONST_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"

# ensure that the azure system is running in arm mode
# this command takes 1.5 seconds to run and could be executed before every azure call is issues arise with other processes that set the mode to asm
subprocess.Popen('azure config mode arm', shell=True).wait()


# Enable CORS for Flask
# http://flask.pocoo.org/snippets/56/
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



#
# Quick way to test that the services are running
#
@app.route("/", methods=['GET', 'POST'])
def greetings():
	return "The Creator"

#
# Generates a unique name, creates Azure resources with the name, and makes an entry in the ledger
#
@app.route("/allocate", methods=['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def create():

	str_useremail = request.form['email'].lower()   # obtain email address from post form (will throw 400 Bad Request if not defined)
	str_userAgent = request.headers.get('User-Agent')

	if ('@' not in parseaddr(str_useremail)[1]):
		log.info("Invalid Email: [" + str_useremail + "]")
		abort(400)

	log.info("Email is: [" + str_useremail + "]")
	log.info("User-Agent is: [" + str_userAgent + "]")

	#check if email has already been allocted and if time span has not been exceeded
	try:
		r = redis.StrictRedis(host='localhost', port=6379, db=0)

		# determine if this user already has a test environment  
		for key in r.scan_iter():
			dkey = key.decode('utf-8')
			jobj = json.loads(r.get(dkey).decode('utf-8'))
			ttl = datetime.strptime(jobj[JSON_TTL], CONST_TIME_FMT)
			created_at = datetime.strptime(jobj[JSON_CREATED_AT], CONST_TIME_FMT)
			if(str_useremail == jobj[JSON_EMAIL]):
				if(ttl > datetime.utcnow()):
					#this user already has an allocated test system, so just reset the TTL (but not past a maximum alloted time) and return the original key
					newttl = datetime.utcnow() + CONST_TIMEDELTA_TO_LIVE_MINUTES
					if(newttl - created_at > CONST_MAXTIMEDELTA_TO_LIVE_MINUTES) :
						newttl = created_at + CONST_MAXTIMEDELTA_TO_LIVE_MINUTES

					jobj[JSON_TTL] = '' + newttl.strftime(CONST_TIME_FMT)[:-3]
					r.set(dkey, json.dumps(jobj))
					log.info("User: [" + str_useremail + "] alread has an allocated system:" + str(r.get(dkey)));
					return json.dumps({'id': dkey, 'minutesleft': str((newttl - datetime.utcnow()).seconds//60) })

		# We will allocate a new test system
		# First check if we have reached the maximum number of allocated test systems
		allocatedSystems = r.dbsize()
		if(allocatedSystems >= CONST_MAX_ALLOCATED_SYSTEMS):
			log.error("The number of allocated Test Flight systems has reached maximum:")
			return "The number of allocated Test Flight systems has reached maximum.  Please try again in a few hours:", 202 



		randName = str(uuid.uuid4()) # generate unique name for the resources
		# data structure we store in redis for TTL enforcement later
		reapor_data = {
			JSON_RESOURCE_GROUP_NAME : randName,
	   		JSON_CREATED_AT : ''+datetime.utcnow().strftime(CONST_TIME_FMT)[:-3],
	   		JSON_EMAIL : str_useremail,
	   		JSON_TTL : ''+(datetime.utcnow() + CONST_TIMEDELTA_TO_LIVE_MINUTES).strftime(CONST_TIME_FMT)[:-3]
		}

		str_minutesleft = str(CONST_TIMEDELTA_TO_LIVE_MINUTES.seconds//60)

		#create resources and save audit to redis
		#create random names for various configuration parameters
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
		
		#write the configuration parameters out to a file
		param_out = open(output_filename,"w")
		param_out.write(json.dumps(data))
		param_out.close()

		#invoke Azure deployment via Azure CLI
		bashCommand = "create.bat " + randName + " " + output_filename
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd=app.root_path)
		output = process.communicate()[0]
		str_output = output.decode('UTF-8')
		# log.info("result of running azure cli:" + str_output)

		if('Succeeded' in str_output):
			#audit the creation event information in Redis for the reapor.py program to clean up later
			r = redis.StrictRedis(host='localhost', port=6379, db=0)
			r.set(randName, json.dumps(reapor_data))
			log.info("created resource " + str(r.get(randName)));
			return json.dumps({'id': randName, 'minutesleft': str_minutesleft })
		else:
			log.error("Resource Group creation did not return success:")
			log.error(str(str_output))
			abort(500)
	except:
		e = sys.exc_info()
		log.error(e)
		abort(500)


#
# Retrieves details about a the specified resource group from Azure
#
@app.route("/status/<kuuid>", methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getResourceDetails(kuuid):
	result = {}

	#ensure resource exists in Redis
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	item = r.get(kuuid)
	if not item:
		log.info("getResourceDetails: " + str(item) + " does not exist")
		abort(404)

	log.info("getResourceDetails: retrieved " + str(item) + " successfully")

	#retrieve resource group deploy state via azure
	# ex. azure group deployment show "629340b2-7447-4737-9143-9a7ba79eaa4f" 
	bashCommand = "get_provisioning_state.bat " + kuuid
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd=app.root_path)
	output = process.communicate()[0]

	str_lines = output.decode('UTF-8').splitlines()

	str_state = CONST_AZURE_STATUS_FAILED
	#parse the results and determine if the deployment is finished yet
	for str_line in str_lines:
		if CONST_AZURE_PROVISIONING_STATE in str_line:
			str_state = str_line.split(":")[2].strip()

	jobj = json.loads(item.decode('utf-8'))
	ttl = datetime.strptime(jobj[JSON_TTL], CONST_TIME_FMT)
	
	str_minutesleft = "0"
	if(ttl > datetime.utcnow()):
		str_minutesleft = str((ttl - datetime.utcnow()).seconds//60)

	# return just the unique names with status information back to the requestor
	return json.dumps({ 
	  "status" : str_state, 
	  'minutesleft': str_minutesleft, 
	  "hosts" : 
      [
      {
 		"hostname" : "kvm1-" + kuuid + ".westus.cloudapp.azure.com" + ":50001", 
 		"username" : "kuser", 
 		"password" : "83GHd1kld803"
 	  },
 	  {
 		"hostname" : "kvm2-" + kuuid + ".westus.cloudapp.azure.com" + ":50001", 
 		"username" : "kuser", 
 		"password" : "83GHd1kld803"
 	  },
 	  {
 		"hostname" : "kvm3-" + kuuid + ".westus.cloudapp.azure.com" + ":50001", 
 		"username" : "kuser", 
 		"password" : "83GHd1kld803"
 	  },
 	  ]
 	})

#
# Terminates a specific resource group from Azure
#
@app.route("/resources/<kuuid>", methods=['DELETE'])
def delete(kuuid):
#	bashCommand = "delete.bat " + kuuid
#	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='app.root_path')
#	output = process.communicate()[0]
#	return output
	abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
