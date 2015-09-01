:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Creates a resource group of 3 machines based off an existing image, and given a name as a parameter (no spaces)
:: 
:: Example:
:: create.bat K83jd-ke83hf-kE308-23Zlsie-03kd1
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

azure group create --json "%1" "West US" -f azuredeploy.json -d "testDeploy" -e azuredeploy.parameters.json