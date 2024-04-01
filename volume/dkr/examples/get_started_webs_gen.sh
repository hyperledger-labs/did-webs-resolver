#!/bin/bash

# controller
ctrlName=$1
# host path
hostPath=$2
# aid
aid=$3

# generate controller did:webs for EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP at labs.hyperledger.org
dkr did webs generate --name "${ctrlName}" --did "did:webs:${hostPath}:${aid}" --meta True