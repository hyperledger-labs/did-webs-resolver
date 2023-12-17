#!/bin/bash

# init environment for controller AID
kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir "/keripy/my-scripts" --config-file my-config

# inception for controller AID
kli incept --name controller --alias controller --file "/keripy/my-scripts/my-incept.json"

# check witness oobi for our AID
curl http://witnesshost:5642/oobi/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha

# generate controller did:webs for labs.hyperledger.org
# dkr did webs generate --name controller --did did:webs:labs.hyperledger.org:did-webs-resolver:pages:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP --oobi http://witnesshost:5642/oobi/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
dkr did webs generate --name controller --did did:webs:labs.hyperledger.org:did-webs-resolver:pages:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP