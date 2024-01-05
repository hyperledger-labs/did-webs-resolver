The public.sh script generates a public attestation of the designated aliases.
It requires a server running at 127.0.0.1:7723 that can serve the schema oobi.
The output will look like:
```
examples $ ./public.sh 
KERI Keystore created at: /usr/local/var/keri/ks/controller
KERI Database created at: /usr/local/var/keri/db/controller
KERI Credential Store created at: /usr/local/var/keri/reg/controller
Prefix  ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
        Public key 1:  DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr

Alias:  controller
Identifier: ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
Seq No: 0

Witnesses:
Count:          0
Receipts:       0
Threshold:      0

Public Keys:
        1. DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr

Waiting for TEL event witness receipts
Sending TEL events to witnesses
Registry:  dAliases(EH6gJT1OQifVBTPsavF5YfkQRODoSAyrMzP4vCeOm0Af) 
        created for Identifier Prefix:  ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
Hit enter after you have added the registry SAID (and maybe attrs, rules, etc) to desig-aliases-public.json
http://127.0.0.1:7723/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5 resolved
Waiting for TEL event witness receipts
Sending TEL events to witnesses
EMIXtMnh1vgYhSBLekbK-360MDcMU10QzejX3zl35q30 has been created.
Current issued credentials for controller (ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe):

Credential #1: EMIXtMnh1vgYhSBLekbK-360MDcMU10QzejX3zl35q30
    Type: Designated Aliases Public Attestation
    Status: Issued ✔
    Issued by ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
    Issued on 2023-11-13T17:41:37.710691+00:00
{"v":"ACDC10JSON0004d5_","d":"EMIXtMnh1vgYhSBLekbK-360MDcMU10QzejX3zl35q30","i":"ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe","ri":"EH6gJT1OQifVBTPsavF5YfkQRODoSAyrMzP4vCeOm0Af","s":"EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5","a":{"d":"ENjmfq8MtWLYncKtb1LYhOdeSvoH6l4u-IJWC6RSmhF2","dt":"2023-11-13T17:41:37.710691+00:00","ids":["did:webs:example.org:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"]},"r":{"d":"EEVTx0jLLZDQq8a5bXrXgVP0JDP7j8iDym9Avfo8luLw","aliasDesignation":{"l":"The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID."},"usageDisclaimer":{"l":"This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."},"issuanceDisclaimer":{"l":"All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."},"termsOfUse":{"l":"Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."}}}
```