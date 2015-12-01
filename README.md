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
- Install Python Redis lib
	- pip install redis
- Install Flask CORS
	- pip install -U flask-cors
- Run the web services
	- python creator.py
	- try http://localhost:5000/
- (Optional) Setup service on the machine that executes 'python reapor.py' every 10 mins


Usage
----------------

| Method        | URL                                            | Purpose  |
| ------------- | ---------------------------------------------- | -------- |
| GET           | http://localhost:5000/                         | proves the module is running successfully |
| POST          | http://localhost:5000/allocate  param *email*  | Creates a resource with 120min TTL |
| GET           | http://localhost:5000/status/*id*              | Retrieves the credentials for a specific resources |

