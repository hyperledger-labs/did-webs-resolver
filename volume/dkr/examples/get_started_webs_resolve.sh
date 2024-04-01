#!/bin/bash

# controller
ctrlName=$1
# did
did=$2
# metadata
meta=$3

# generate controller did:webs for EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP at labs.hyperledger.org
dkr did webs resolve --name "${ctrlName}" --did "${did}" --meta "${meta}"
