#!/bin/bash

#cd ./volume/dkr/examples

kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir ./my-scripts --config-file config-docker

kli incept --name controller --alias controller --file ./my-scripts/incept.json

dkr did webs generate --name controller --did "did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"