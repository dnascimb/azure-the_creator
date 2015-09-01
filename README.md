# azure-the_creator
=====================================================
Utilities supporting the creation of Azure resources using Azure CLI/ARM/Python/Flask.

Instructions:
-------------

- Install Azure CLI (https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-azure-resource-manager/)
- Authenticate via CLI (https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-connect/)
	- azure config mode arm
	- azure login -u <username>
- Install Python (v2 or v3)
- Install Flask
- Install Redis
- Run the web services
	- $ python webservices.py
	- try http://localhost:5000/create
- (Optional) Setup service on the machine that executes 'python reapor.py' every 1 min


Usage
----------------

**POST** http://URL/create
Creates a resource group with a 30min TTL


**DELETE** http://URL/delete/<machine_name>
Deletes a resource group