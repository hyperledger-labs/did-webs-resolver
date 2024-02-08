#!/bin/bash

#cd ./volume/dkr/examples

AID="$1"
NAME="resolver"

# Run the command and capture the output
output=$(kli status --name $NAME)

# Check the output
if [[ $output == *"Keystore must already exist, exiting"* ]]; then
    echo ""
    read -p "Press enter to setup $NAME environment..."

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

echo ""
read -p "Press enter to resolve did:webs..."

dkr did webs resolve --name $NAME --did "did:webs:did-webs-service%3a7676:$AID"


