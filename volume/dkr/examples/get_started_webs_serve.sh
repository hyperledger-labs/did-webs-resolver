#!/bin/bash

#controller
ctrlName=$1
#/keripy/my-scripts
configDir=$2
#my-config
configFile=$3

# serve controller did:webs for EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP at 127.0.0.1:
dkr did webs service --name "${ctrlName}" --config-dir "${configDir}" --config-file "${configFile}"
sleep 5

pid=$!
echo "dkr did webs service running as pid: $pid"