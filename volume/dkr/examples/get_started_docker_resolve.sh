#!/bin/bash

#cd ./volume/dkr/examples

if [ -z "$1" ]; then
    AID="ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
else
    AID="$1"
fi

NAME="resolver"

# Run the command and capture the output
output=$(kli status --name $NAME)

# Check the output
if [[ $output == *"Keystore must already exist, exiting"* ]]; then
    echo "Setting up $NAME environment..."

    kli init --name $NAME --salt 0AAQmsjh-C7kAJZQEaaaaaaa --nopasscode --config-dir /usr/local/var/webs/volume/dkr/examples/my-scripts --config-file config-docker
    kli incept --name $NAME --alias $NAME --file /usr/local/var/webs/volume/dkr/examples/my-scripts/incept.json

    output=$(kli status --name lance)
    if [[ $output != *"Keystore must already exist, exiting"* ]]; then
        echo "Setup is confirmed."
    fi
else
    echo "Keystore already set up. Setup is confirmed."
    # Place the commands you want to run if the keystore already exists here
fi

DID="did:webs:did-webs-service%3a7676:$AID"

echo "Resolving $AID did:webs $DID... "
source "./get_started_webs_resolve.sh" "${NAME}" "${DID}" "True"


