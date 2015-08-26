:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Creates a resource group of 3 machines based off an existing image
::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

azure group create "djnSimpleMachineTest" "West US" -f azuredeploy.json -d "testDeploy" -e azuredeploy.parameters.json