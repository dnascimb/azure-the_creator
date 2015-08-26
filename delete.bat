:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: This module's purpose is to delete a previously created resource group
::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: C:\github\azure-the_creator>azure group delete -h
:: help:    Deletes a resource group
:: help:
:: help:    Usage: group delete [options] <name>
:: help:
:: help:    Options:
:: help:      -h, --help                     output usage information
:: help:      -v, --verbose                  use verbose output
:: help:      --json                         use json output
:: help:      -n --name <name>               the resource group name
:: help:      -q, --quiet                    quiet mode (do not ask for delete confirmation)
:: help:      --subscription <subscription>  the subscription identifier

azure group delete -q --json -n "djnSimpleMachineTest"