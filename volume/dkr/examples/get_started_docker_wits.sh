#!/bin/bash

#cd ./volume/dkr/examples

kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir /usr/local/var/webs/volume/dkr/examples/my-scripts --config-file config-docker

kli oobi resolve --name controller --oobi-alias wan --oobi "http://witnesshost:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller"
kli oobi resolve --name controller --oobi-alias wil --oobi "http://witnesshost:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller"
kli oobi resolve --name controller --oobi-alias wes --oobi "http://witnesshost:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller"

kli incept --name controller --alias controller --file /usr/local/var/webs/volume/dkr/examples/my-scripts/incept-wits.json

echo ""
read -p "Press enter to generate did:webs..."

AID="EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP"
dkr did webs generate --name controller --did "did:webs:did-webs-service%3a7676:$AID"

echo ""
read -p "Press enter to copy to pages..."

cp -R $AID ../pages/

echo ""
echo "ATTENTION: In your did-webs-service, start the webs server first, see the GETTING_STARTED.md for those instructions"
read -p "Press enter to resolve did:webs..."

dkr did webs resolve --name controller --did "did:webs:did-webs-service%3a7676:$AID" --meta True

echo ""
read -p "Press enter to create designated aliases..."

kli vc registry incept --name controller --alias controller --registry-name dAliases

kli oobi resolve --name controller --oobi-alias myDesigAliases --oobi "https://weboftrust.github.io/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"

kli vc issue --name controller --alias controller --registry-name dAliases --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5 --data @desig-aliases-attr-public.json --rules @desig-aliases-rules-public.json

kli vc list --name controller --alias controller --issued --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5

SAID=$(kli vc list --name controller --alias controller --issued --said --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5)

kli vc export --name controller --alias controller --said "$SAID" --chain

echo ""
read -p "Press enter generate did:webs with designated aliases..."

dkr did webs generate --name controller --did "did:webs:did-webs-service%3a7676:$AID"

cp -R $AID ../pages/

echo ""
read -p "Press enter to resolve did:webs with designated aliases..."

dkr did webs resolve --name controller --did "did:webs:did-webs-service%3a7676:$AID" --meta True