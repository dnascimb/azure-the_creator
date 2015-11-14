:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: This module's purpose is to delete a blobs (VHDs, status files) that is not deleted by default when you delete virtual machines
::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: C:\github\azure-the_creator>azure storage blob delete -h
:: help:    Delete the specified storage blob
:: help:
:: help:    Usage: storage blob delete [options] [container] [blob]
:: help:
:: help:    Options:
:: help:      -h, --help                                  output usage information
:: help:      -v, --verbose                               use verbose output
:: help:      --json                                      use json output
:: help:      --container <container>                     the storage container name
:: help:      -b, --blob <blobName>                       the storage blob name
:: help:      --sas <sas>                                 the shared access signature of the storage container or blob
:: help:      -q, --quiet                                 remove the specified Storage blob without confirmation
:: help:      -a, --account-name <accountName>            the storage account name
:: help:      -k, --account-key <accountKey>              the storage account key
:: help:      -c, --connection-string <connectionString>  the storage connection string
:: help:      -vv                                         run storage command in debug mode
:: help:
:: help:    Current Mode: arm (Azure Resource Management)

azure storage blob delete --container vhds --blob %1 -a %2 -k "%~3" -q
