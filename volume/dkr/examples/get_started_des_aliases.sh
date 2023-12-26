#!/bin/bash

# # updates the SAIDs of the schemas
# ../update.sh

alias="controller"
reg_name="dAliases"
d_alias_schema="EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"
# da_schema_oobi="http://127.0.0.1:7723/oobi/${d_alias_schema}"
da_schema_oobi="https://weboftrust.github.io/oobi/${d_alias_schema}"

#clear state from previous runs
echo "Clearing state from previous runs for $alias"
find /usr/local/var/keri/* -name "$alias" -type d -exec rm -rf {} + 2>/dev/null
find /usr/local/var/keri/* -name "$reg_name" -type d -exec rm -rf {} + 2>/dev/null

echo "Initializing $alias"
kli init --name "$alias" --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir "./my-scripts" --config-file config
echo "Incepting $alias"
kli incept --name "$alias" --alias "$alias" --file "./my-scripts/my-incept.json"
echo "Getting $alias status"
kli status --name "$alias" --alias "$alias"

echo "Creating registry $reg_name"
kli vc registry incept --name "$alias" --alias "$alias" --registry-name "$reg_name"

echo "Saidifying attestation rules"
kli saidify --file ./desig-aliases-rules-public.json --label "d"
echo "Saidifying attestation attributes"
kli saidify --file ./desig-aliases-attr-public.json --label "d"

# manually add rules example SAID and attribute example SAID to the desig-aliases.json
# read -p "Hit enter after you have added the registry SAID (and maybe attrs, rules, etc) to desig-aliases-public.json"
# echo "Saidifying attestation with the registry you added"
# kli saidify --file ./desig-aliases-public.json --label "d"

echo "Resolving schema at $da_schema_oobi"
kli oobi resolve --name "$alias" --oobi-alias myDesigAliases --oobi "$da_schema_oobi"
echo "Issuing attestation to registry $reg_name with schema $d_alias_schema from attr file desig-aliases-attr-public.json"
kli vc issue --name "$alias" --alias "$alias" --registry-name "$reg_name" --schema "${d_alias_schema}" --data @desig-aliases-attr-public.json --rules @desig-aliases-rules-public.json
# kli vc create --name "$alias" --alias "$alias" --registry-name "$reg_name" --schema "${d_alias_schema}" --credential @desig-aliases-public.json
echo "Getting SAID for attestation in registry $reg_name with schema $d_alias_schema"
SAID=$(kli vc list --name "$alias" --alias "$alias" --issued --said --schema "${d_alias_schema}")
echo "Listing attestations in registry $reg_name with schema $d_alias_schema"
kli vc list --name "$alias" --alias "$alias" --issued --schema "${d_alias_schema}"

echo "Exporting attestation with SAID $SAID"
kli vc export --name "$alias" --alias "$alias" --said "${SAID}" --chain