#!/bin/bash
# set -x

# RUN cd /usr/local/var/webs/volume/dkr/examples
# RUN ./get_started_create_id.sh "controller" "./my-scripts" "config-docker" "incept-wits.json"
# RUN ./get_started_webs_gen.sh "controller" "did-webs-service%3a7676" "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP"

#controller
ctrlName=$1
#salt
ctrlSalt=$2
#./my-scripts
configDir=$3
#my-config
configFile=$4
#./my-scripts/my-incept.json
inceptFile=$5

echo "Init KERI id config file at ${configDir}/keri/cf/${configFile} contains:"
cat "${configDir}/keri/cf/${configFile}.json"

# init environment for controller AID
kli init --name "${ctrlName}" --salt "${ctrlSalt}" --nopasscode --config-dir "${configDir}" --config-file "${configFile}"

echo "Incept KERI id config file at ${inceptFile} contains:"
cat "${inceptFile}"

# inception for controller AID
kli incept --name "${ctrlName}" --alias "${ctrlName}" --file "${inceptFile}"

# see status
kli status --name "${ctrlName}"