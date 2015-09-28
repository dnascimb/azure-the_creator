from flask import Flask
from datetime import datetime, timedelta
from flask.ext.cors import CORS, cross_origin
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
@app.route("/", methods=['GET'])
def greetings():
	return "The Creator"

#
# Generates a unique name, creates Azure resources with the name, and makes an entry in the ledger
#
@app.route("/resources", methods=['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def create():
	randName = str(uuid.uuid4()) # generate unique name for the resources
	reapor_data = {
		'resource_group_name' : randName,
   		'created_at' : ''+datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
   		'ttl' : ''+(datetime.utcnow() + timedelta(minutes=60)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	}

	#create resources and save audit to redis
	try:
		#generate random names for various configuration parameters
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
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
		output = process.communicate()[0]
		str_output = output.decode('UTF-8')
		log.info("result of running azure cli:" + str_output)

		if('Succeeded' in str_output):
			#audit the creation event information in Redis for the reapor.py program to clean up later
			r = redis.StrictRedis(host='localhost', port=6379, db=0)
			r.set(randName, json.dumps(reapor_data))
			log.info("created resource " + str(r.get(randName)));
			return json.dumps({'id': randName})
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
@app.route("/resources/<kuuid>", methods=['GET'])
def getResourceDetails(kuuid):
	result = {}

	#ensure resource exists in Redis
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	item = r.get(kuuid)
	if not item:
		log.info("getResourceDetails: " + str(item) + " does not exist")
		abort(404)

	log.info("getResourceDetails: retrieved " + str(item) + " successfully")

	#retrieve resource group deploy log via azure
	# ex. azure group log show "629340b2-7447-4737-9143-9a7ba79eaa4f" --last-deployment
	bashCommand = "get_resource_log.bat " + kuuid
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
	output = process.communicate()[0]
	str_output = output.decode('UTF-8')

	#parse the results and determine how many components have not finished yet
	#node = locateByName(str_output, 'status')
	#print node['value']

	#calculate a percentage or failure to return;
	return json.dumps({ 
	  "status" : "Deployed", 
	  "progress" : "100%",
	  "hosts" : 
      [
      {
 		"hostname" : "kvm1-" + kuuid + ":50001", 
 		"username" : "kuser", 
 		"password" : "83GHd1kld803"
 	  },
 	  {
 		"hostname" : "kvm2-" + kuuid + ":50001", 
 		"username" : "kuser", 
 		"password" : "83GHd1kld803"
 	  },
 	  {
 		"hostname" : "kvm3-" + kuuid + ":50001", 
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
	bashCommand = "delete.bat " + kuuid
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
	output = process.communicate()[0]
	return output

#
# Function to recursively tree-search until a name is found
#
def locateByName(e,name):
    if e.get('name',None) == name:
        return e

    for child in e.get('children',[]):
        result = locateByName(child,name)
        if result is not None:
            return result

    return None



if __name__ == "__main__":
    app.run()
