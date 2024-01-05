#!/bin/bash

# need to run witness network
rm -Rf /usr/local/var/keri/*;rm -Rf ~/.keri/*;kli witness demo &
wpid=$!
echo "witness pid: $wpid"

# init environment for controller AID
kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir "./my-scripts" --config-file local

# inception for controller AID
kli incept --name controller --alias controller --file "./my-scripts/incept-local.json"

# check witness oobi for our AID
curl http://127.0.0.1:5642/oobi/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha

# generate controller did:webs for labs.hyperledger.org
dkr did webs generate --name controller --did did:webs:labs.hyperledger.org:did-webs-resolver:pages:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP --oobi http://127.0.0.1:5642/oobi/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
# dkr did webs generate --name controller --did did:webs:labs.hyperledger.org:did-webs-resolver:pages:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP

kill $wpid