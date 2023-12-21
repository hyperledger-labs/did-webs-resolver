#!/bin/bash

#controller
ctrlName=$1
#/keripy/my-scripts
configDir=$2
#my-config
configFile=$3
#my-incept.json
inceptFile=$4

# init environment for controller AID
kli init --name "${ctrlName}" --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir "${configDir}" --config-file "${configFile}"

# inception for controller AID
kli incept --name "${ctrlName}" --alias "${ctrlName}" --file "${configDir}/${inceptFile}"