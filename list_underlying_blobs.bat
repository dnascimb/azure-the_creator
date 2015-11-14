:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: This module's purpose is to find underlying blobs (VHDs, status files) that are not deleted by default when you delete virtual machines
::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: C:\github\azure-the_creator>azure storage blob list -h
:: help:    List storage blob in the specified storage container use wildcard and blob name prefix
:: help:
:: help:    Usage: storage blob list [options] [container] [prefix]
:: help:
:: help:    Options:
:: help:      -h, --help                                  output usage information
:: help:      -v, --verbose                               use verbose output
:: help:      --json                                      use json output
:: help:      --container <container>                     the storage container name
:: help:      -p, --prefix <prefix>                       the blob name prefix
:: help:      --sas <sas>                                 the shared access signature of the storage container
:: help:      -a, --account-name <accountName>            the storage account name
:: help:      -k, --account-key <accountKey>              the storage account key
:: help:      -c, --connection-string <connectionString>  the storage connection string
:: help:      -vv                                         run storage command in debug mode
@echo off
azure storage blob list --json --container vhds --prefix %1 -a %2 -k "%~3"