#!/bin/bash

#cd ./volume/dkr/examples

kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir /usr/local/var/webs/volume/dkr/examples/my-scripts --config-file config-docker

kli incept --name controller --alias controller --file /usr/local/var/webs/volume/dkr/examples/my-scripts/incept.json

echo ""
read -p "Press enter to generate did:webs..."

dkr did webs generate --name controller --did "did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe" --meta True

echo ""
read -p "Press enter to copy to pages..."

cp -R ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe ../pages/