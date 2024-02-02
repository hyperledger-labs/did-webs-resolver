# Developers - Getting Started

Welcome to the `did:webs` reference implementation Getting Started guide.

Thank you to Markus Sabadello @peacekeeper from DanubeTech who created the original guide for IIW37 [here](https://github.com/peacekeeper/did-webs-iiw-tutorial)

If you're running into trouble in the process below, be sure to check the section [Trouble Shooting](#trouble-shooting) below. 

Let's get started! We'll use docker to setup and run in a simple environment.

## Run Docker build
```
docker compose build --no-cache
```

## Run Docker containers for the keri witness network and the `did:webs` generator and resolver environment

```
docker compose down
docker compose up -d
```

## Enter the dkr docker environment command line to begin running keri, etc. commands

```
docker compose exec webs /bin/bash
```

## Create your KERI identifier
Execute the following commands to create your KERI identifier that secures your did:webs DID:
* From the dkr Docker container shell, go to the `examples` dir
```
cd volume/dkr/examples
```

### Create a cryptographic salt to secure your KERI identifier
```
kli salt
```
The example salt we use in the scripts:
```
0AAQmsjh-C7kAJZQEzdrzwB7
```


### Create the KERI AID ```ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe```
#### initialize your environment with a name, salt, and config file

`command:`
```
kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir /usr/local/var/webs/volume/dkr/examples/my-scripts --config-file config-docker
```

```output:```
```
KERI Keystore created at: /usr/local/var/keri/ks/controller
KERI Database created at: /usr/local/var/keri/db/controller
KERI Credential Store created at: /usr/local/var/keri/reg/controller

Loading 3 OOBIs...
http://witnesshost:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller succeeded
http://witnesshost:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller succeeded
http://witnesshost:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller succeeded 
```

#### create your AID by creating it's first event, the inception event

`command:`
```
kli incept --name controller --alias controller --file /usr/local/var/webs/volume/dkr/examples/my-scripts/incept.json
```

`output:`
```
Prefix  ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
        Public key 1:  DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr
```
Your AID is ```ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe``` and your current public key is ```DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr```

#### Additional info
The AID config-file in the container is at ./my-scripts/keri/cf/config-docker.json and contains the KERI OOBIs of the witnesses that we'll use:
In this case they are available from the witness network that we started in the docker-compose. If you `cat` the config at `/usr/local/var/webs/volume/dkr/examples/my-scripts/keri/cf/config-docker.json` you should see:

`command`
```
cat /usr/local/var/webs/volume/dkr/examples/my-scripts/keri/cf/config-docker.json
```

`config:`
```json
{
  "dt": "2022-01-20T12:57:59.823350+00:00",
  "iurls": [
    "http://witnesshost:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller",
    "http://witnesshost:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller",
    "http://witnesshost:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller"
  ]
}
```

## (Optional) Perform more KERI operations

Optionally use `kli` to perform additional KERI operations such as key rotation, threshold signatures, etc., see KERI docs for details.

See [a key rotation example](#example-key-rotation) below.


## Decide your web address for did:webs

Find a web address (host, optional port, optional path) that you control.

Example web address with host `labs.hyperledger.org`, no optional port, and optional path `pages`:

`web example url`
```
https://labs.hyperledger.org/did-webs-resolver/pages/
```

`docker example url`
```
http://did-webs-service%3a7676
```

## Generate your did:webs identifier files using your KERI AID

Note: Replace with your actual web address and AID

You should pick the web address (host, optional port, optional path) where you will host the did:webs identifier. For this example we'll use the docker service we've created at host `did-webs-service` and with optional port `7676`. NOTE the spec requires the colon `:` before an optional port to be encoded as `%3a` in the did:webs identifier.

`command:`
```
dkr did webs generate --name controller --did "did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
```

`output:`
```
Generating CESR event stream data from hab
Generating ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe KEL CESR events
Writing CESR events to ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe/keri.cesr: 
{"v":"KERI10JSON00012b_","t":"icp","d":"ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe","i":"ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe","s":"0","kt":"1","k":["DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr"],"nt":"1","n":["ELa775aLyane1vdiJEuexP8zrueiIoG995pZPGJiBzGX"],"bt":"0","b":[],"c":[],"a":[]}-VAn-AABAADjfOjbPu9OWce59OQIc-y3Su4kvfC2BAd_e_NLHbXcOK8-3s6do5vBfrxQ1kDyvFGCPMcSl620dLMZ4QDYlvME-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2023-12-26T20c12c58d336072p00c00

  "didDocument": {
    "id": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
    "verificationMethod": [
      {
        "id": "#DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
        "type": "JsonWebKey",
        "controller": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
        "publicKeyJwk": {
          "kid": "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
          "kty": "OKP",
          "crv": "Ed25519",
          "x": "evT4j6Yw3uHpwsw5NEmSR8-4x3S-BA-s6Thjd51oeOs"
        }
      }
    ],
    "service": [],
    "alsoKnownAs": []
  }
  ... with additional output continuing...
```

This creates files `did.json` and `keri.cesr` under local path `./volume/dkr/examples/<your AID>/did.json`

You can access these files either from within your Docker container or on your local computer filesystem.
- `<local path on computer to did-webs-resolver>/volume/dkr/examples/<your AID>` (local path on your computer)
- `/usr/local/var/webs/volume/dkr/examples/<your AID>` (local path in the Docker container)

`command:`
```
cat ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe/did.json
```

`output:`
```
{"id": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe", "verificationMethod": [{"id": "#DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr", "type": "JsonWebKey", "controller": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe", "publicKeyJwk": {"kid": "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr", "kty": "OKP", "crv": "Ed25519", "x": "evT4j6Yw3uHpwsw5NEmSR8-4x3S-BA-s6Thjd51oeOs"}}], "service": [], "alsoKnownAs": []}
```

## Upload did.json and keri.cesr to the web address (host, optional port, optional path) that you chose

E.g. using git, Github pages, FTP, SCP, etc.

## Example: serve from docker
You can run the docker example service to serve the did.json and keri.cesr files for the other docker containers:

First, lets copy our generated files to the directory we'll serve from. On your `LOCAL` machine (or within the container) you can copy `volume/dkr/examples/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe` to `volume/dkr/pages/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe`:

```
cp -R volume/dkr/examples/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe volume/dkr/pages/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
```

Now lets go into our did-webs-service docker container:
```
docker compose exec did-webs-service /bin/bash
```

```
dkr did webs service --name webserve --config-dir /usr/local/var/webs/volume/dkr/examples/my-scripts --config-file config-docker
```

It will search for AID named directories and for the two files (`did.json` and `keri.cesr`) under those directories. The search occurs from the directory specified in the config-file properties:
```
    "keri.cesr.dir": "/usr/local/var/webs/volume/dkr/pages/",
    "did.doc.dir": "/usr/local/var/webs/volume/dkr/pages/"
```

And when a file is found by the service, there will be logs like:
```
Looking for did.json file /usr/local/var/webs/volume/dkr/pages/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
registering /ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe/did.json
```

It will serve it at a URL that you can CURL from any of our docker containers (for instance from the webs container) like:

`command:`
```
curl -GET http://did-webs-service:7676/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe/did.json
```

`output:`
```
{
  "id": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
  "verificationMethod": [
    {
      "id": "#DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
      "type": "JsonWebKey",
      "controller": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
      "publicKeyJwk": {
        "kid": "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "evT4j6Yw3uHpwsw5NEmSR8-4x3S-BA-s6Thjd51oeOs"
      }
    }
  ],
  "service": [],
  "alsoKnownAs": []
}
```

`command:`
```
curl -GET http://did-webs-service:7676/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe/keri.cesr
```

`KERI CESR output:`
```
"{\"v\":\"KERI10JSON00012b_\",\"t\":\"icp\",\"d\":\"ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe\",\"i\":\"ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe\",\"s\":\"0\",\"kt\":\"1\",\"k\":[\"DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr\"],\"nt\":\"1\",\"n\":[\"ELa775aLyane1vdiJEuexP8zrueiIoG995pZPGJiBzGX\"],\"bt\":\"0\",\"b\":[],\"c\":[],\"a\":[]}-VAn-AABAADjfOjbPu9OWce59OQIc-y3Su4kvfC2BAd_e_NLHbXcOK8-3s6do5vBfrxQ1kDyvFGCPMcSl620dLMZ4QDYlvME-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2024-01-02T14c12c15d456835p00c00"
```

### Example: Resolve AID as did:webs using local resolver

Back in the webs docker container, you can resolve the DID from the did-webs-service:

Resolve the did:webs for the `controller` did:
```
dkr did webs resolve --name controller --did "did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
```

### Example: Add designated aliases attestation

Because your AID can be served as a did:webs, did:web, did:keri, etc. identifier you can specify these are designated aliases for verification and discovery purposes.
To create this designated aliases attestation, you can the following:

`create credential registry command:`
```
kli vc registry incept --name controller --alias controller --registry-name dAliases
```

`output:`
```
Waiting for TEL event witness receipts
Sending TEL events to witnesses
Registry:  dAliases(EIHt7YgiLNzFCZ4k4LxdZ7ASJcFo1-vkoZERMHzq87HL) 
        created for Identifier Prefix:  ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
```

All ACDC credentials/attestations require a schema. Lets resolve the schema for the designated aliases attestation:

`command:`
```
kli oobi resolve --name controller --oobi-alias myDesigAliases --oobi "https://weboftrust.github.io/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"
``` 

`output:`
```
https://weboftrust.github.io/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5 resolved
```

We provide the attestation rules and attributes under  `volume/dkr/examples`
```
cd volume/dkr/examples/
```

You can issue the attestation using the following command, supplying the registry name, schema, attestation attributes and rules:

`command:`
```
kli vc issue --name controller --alias controller --registry-name dAliases --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5 --data @desig-aliases-attr-public.json --rules @desig-aliases-rules-public.json
```

`output:`
```
Writing credential EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ to credential.json
Waiting for TEL event witness receipts
Sending TEL events to witnesses
Credential issuance complete, sending to recipient
EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ has been issued.
```

To see the attestation you can list the credentials for the registry:

`command:`
```
kli vc list --name controller --alias controller --issued --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5
```

`output:`
```
Current issued credentials for controller (ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe):

Credential #1: EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ
    Type: Designated Aliases Public Attestation
    Status: Issued ✔
    Issued by ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
    Issued on 2023-11-13T17:41:37.710691+00:00
```

To see the the raw ACDC attestation, you can use the following command:

`command (Note replace <YOUR_REGISTRY>, for example with EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ):`
```
kli vc export --name controller --alias controller --said <YOUR_REGISTRY> --chain
```

`output:`
```json
{
    "v": "ACDC10JSON0005f2_",
    "d": "EFDyKtexrWI2-omP6oSKxcssDAtC-fsCFsxp0B7TgHhB",
    "i": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
    "ri": "EO0BjjT__dWwnO86tCJ2_MG3_7PUqG1RD_ZaY5hM2k6U",
    "s": "EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5",
    "a": {
        "d": "EJJjtYa6D4LWe_fqtm1p78wz-8jNAzNX6aPDkrQcz27Q",
        "dt": "2023-11-13T17:41:37.710691+00:00",
        "ids": [
            "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
            "did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
            "did:web:example.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
            "did:web:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
            "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
        ]
    },
    "r": {
        "d": "EEVTx0jLLZDQq8a5bXrXgVP0JDP7j8iDym9Avfo8luLw",
        "aliasDesignation": {
            "l": "The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID."
        },
        "usageDisclaimer": {
            "l": "This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."
        },
        "issuanceDisclaimer": {
            "l": "All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."
        },
        "termsOfUse": {
            "l": "Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."
        }
    }
}
```

Now if we re-generate our did:webs identifier the did.json and keri.cesr files will include the attestation information:

`command:`
```
dkr did webs generate --name controller --did "did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
```

```introductory output:```
```
Generating CESR event stream data from hab
Generating ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe KEL CESR events
Generating EO0BjjT__dWwnO86tCJ2_MG3_7PUqG1RD_ZaY5hM2k6U TEL CESR events
Generating EFDyKtexrWI2-omP6oSKxcssDAtC-fsCFsxp0B7TgHhB TEL CESR events
Generating EFDyKtexrWI2-omP6oSKxcssDAtC-fsCFsxp0B7TgHhB ACDC CESR events, issued by ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
Writing CESR events to ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe/keri.cesr....
```

The KERI CESR output has our original `icp` inception event with our AID and current/next key:

```json
{
  "v": "KERI10JSON00012b_",
  "t": "icp",
  "d": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
  "i": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
  "s": "0",
  "kt": "1",
  "k": [
    "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr"
  ],
  "nt": "1",
  "n": [
    "ELa775aLyane1vdiJEuexP8zrueiIoG995pZPGJiBzGX"
  ],
  "bt": "0",
  "b": [],
  "c": [],
  "a": []
}
```

And the new interaction `ixn` event for the registry:
```json
{ 
  "v": "KERI10JSON00013a_",
  "t": "ixn",
  "d": "EL-g0526QJTIIUXmFkgE_Qsi-xD71jUFb15H5arW6FCJ",
  "i": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
  "s": "1",
  "p": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
  "a": [
    {
      "i": "EIHt7YgiLNzFCZ4k4LxdZ7ASJcFo1-vkoZERMHzq87HL",
      "s": "0",
      "d": "EIHt7YgiLNzFCZ4k4LxdZ7ASJcFo1-vkoZERMHzq87HL"
    }
  ]
}
```

And the new interaction `ixn` event for the attestation:
```json
{
  "v": "KERI10JSON00013a_",
  "t": "ixn",
  "d": "EMRPgyPi_v_Spq211aSBGbVUgisiX-GL-mhWWMGxx8hv",
  "i": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
  "s": "2",
  "p": "EL-g0526QJTIIUXmFkgE_Qsi-xD71jUFb15H5arW6FCJ",
  "a": [
    {
      "i": "EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ",
      "s": "0",
      "d": "EIxW8nKRpp9iAZ1IRT8hWOBGBNXoufWfMWVPUPWscPnA"
    }
  ]
}
```

Inception statement for the Registry
```json
{
    "v": "KERI10JSON000113_",
    "t": "vcp",
    "d": "EIHt7YgiLNzFCZ4k4LxdZ7ASJcFo1-vkoZERMHzq87HL",
    "i": "EIHt7YgiLNzFCZ4k4LxdZ7ASJcFo1-vkoZERMHzq87HL",
    "ii": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
    "s": "0",
    "c": [
        "NB"
    ],
    "bt": "0",
    "b": [],
    "n": "AFn2tXQuaCtqo0Q7QcpciVzDrt_5xqBeZKiN6IQmJTZg"
}
```

Simple Credential (Attestation) Issuance Event `iss`:
```json
{
    "v": "KERI10JSON0000ed_",
    "t": "iss",
    "d": "EIxW8nKRpp9iAZ1IRT8hWOBGBNXoufWfMWVPUPWscPnA",
    "i": "EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ",
    "s": "0",
    "ri": "EIHt7YgiLNzFCZ4k4LxdZ7ASJcFo1-vkoZERMHzq87HL",
    "dt": "2023-11-13T17:41:37.710691+00:00"
}
```

The ACDC attestation anchored to the TEL:
```json
{
    "v": "ACDC10JSON000514_",
    "d": "EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ",
    "i": "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
    "ri": "EIHt7YgiLNzFCZ4k4LxdZ7ASJcFo1-vkoZERMHzq87HL",
    "s": "EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5",
    "a": {
        "d": "EHQgqNNSueVmVjlErrGtzjl-HJya9rMUiNadDSkZQ1kV",
        "dt": "2023-11-13T17:41:37.710691+00:00",
        "ids": [
            "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
            "did:web:example.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
        ]
    },
    "r": {
        "d": "EEVTx0jLLZDQq8a5bXrXgVP0JDP7j8iDym9Avfo8luLw",
        "aliasDesignation": {
            "l": "The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID."
        },
        "usageDisclaimer": {
            "l": "This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."
        },
        "issuanceDisclaimer": {
            "l": "All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."
        },
        "termsOfUse": {
            "l": "Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."
        }
    }
}
```

`The DID document output calls out the equivalentIds and alsoKnownAs identifiers:`
```
Generating DID document for did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe with aid ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe using oobi None and metadata None registry name for creds None
Credential #1: EFDyKtexrWI2-omP6oSKxcssDAtC-fsCFsxp0B7TgHhB
    Type: Designated Aliases Public Attestation
    Status: Issued ✔
    Issued by ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
    Issued on 2023-11-13T17:41:37.710691+00:00
Equivalent DIDs: ['did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe', 'did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe']
Also Known As DIDs: ['did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe', 'did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe', 'did:web:example.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe', 'did:web:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe', 'did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe']
```

And the DID document is now:
```json
{
  "didDocument": {
    "id": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
    "verificationMethod": [
      {
        "id": "#DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
        "type": "JsonWebKey",
        "controller": "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
        "publicKeyJwk": {
          "kid": "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
          "kty": "OKP",
          "crv": "Ed25519",
          "x": "evT4j6Yw3uHpwsw5NEmSR8-4x3S-BA-s6Thjd51oeOs"
        }
      }
    ],
    "service": [],
    "alsoKnownAs": [
      "did:web:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
      "did:webs:did-webs-service%3a7676:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
      "did:web:example.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
      "did:web:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
      "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
    ]
  }
}
```

Now you can copy the `did.json` and `keri.cesr` files to the pages directory again.
```
cp -R volume/dkr/examples/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe volume/dkr/pages/ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe
```

## Example: Using Witnesses

In order to use witnesses we run through the same steps as above but we use a different configuration that assigns witnesses to the AID. Witnesses are a special service endpoint because they are in the inception event (and can be updated in the rotation events).

To execute all of the above quickly we can use the script from the `webs` container you can:

```
cd volume/dkr/examples/ 
```
and execute the following script:

```
./get_started_docker_wits.sh
```

The notable differences now that we are using witnesses:
* The AID is different now `EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP`, because the inception event contians the witness information which modifies the data used to generate the AID.
* The DID Document now lists the witnesses in the service endpoints:
```json
Got DID doc: {
  "id": "did:web:did-webs-service%3a7676:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP",
  "verificationMethod": [
    {
      "id": "#DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
      "type": "JsonWebKey",
      "controller": "did:web:did-webs-service%3a7676:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP",
      "publicKeyJwk": {
        "kid": "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr",
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "evT4j6Yw3uHpwsw5NEmSR8-4x3S-BA-s6Thjd51oeOs"
      }
    }
  ],
  "service": [
    {
      "id": "#BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5642/",
        "tcp": "tcp://witnesshost:5632/"
      }
    },
    {
      "id": "#BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5643/",
        "tcp": "tcp://witnesshost:5633/"
      }
    },
    {
      "id": "#BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5644/",
        "tcp": "tcp://witnesshost:5634/"
      }
    },
    {
      "id": "#BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5642/",
        "tcp": "tcp://witnesshost:5632/"
      }
    },
    {
      "id": "#BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5643/",
        "tcp": "tcp://witnesshost:5633/"
      }
    },
    {
      "id": "#BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5644/",
        "tcp": "tcp://witnesshost:5634/"
      }
    },
    {
      "id": "#BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5642/",
        "tcp": "tcp://witnesshost:5632/"
      }
    },
    {
      "id": "#BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5643/",
        "tcp": "tcp://witnesshost:5633/"
      }
    },
    {
      "id": "#BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesshost:5644/",
        "tcp": "tcp://witnesshost:5634/"
      }
    }
  ],
  "alsoKnownAs": []
}
```
* The KERI Event Stream shows the witnesses in the `b` field of the inception event:
```json
Loading KERI CESR from http://did-webs-service:7676/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/keri.cesr
Got KERI CESR:
{
    "v": "KERI10JSON0001b7_",
    "t": "icp",
    "d": "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP",
    "i": "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP",
    "s": "0",
    "kt": "1",
    "k": [
        "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr"
    ],
    "nt": "1",
    "n": [
        "ELa775aLyane1vdiJEuexP8zrueiIoG995pZPGJiBzGX"
    ],
    "bt": "3",
    "b": [
        "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
        "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
        "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
    ],
    "c": [],
    "a": []
}-VBq-AABAABv33lz0MENsIaM2J1hsbl_8awkJlVT7M1Cnzix0JQSEEwhfSsOt5Wqvuw27wUUKZLCScKoT01FV4WfowFrh_MN-BADAAC_SiZWJFOCuIB_py4gqaMFQtTVWtFCpPfP2LgyqqUS2naTh0nZNlH6MPHSbQNRoImkHnMFrUiBr5ZtwvQ-tNwIABBazaCrt7WQD5Dj1U3KqlZhgOPh7-ca2S0BnRRSEHxW5yoECaC04nyTxYh_wU9TH2WLr14hP-mLHHJDM-wM2esOACA2lyZPmqv2mefIL3orZNm8vb7pyLO5R4zOhHqqXkS1utJrKndiNd4Yu4c6xJnVkc-l6DABB9qe-otLGCkoWDEI-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2024-02-02T14c44c12d081323p00c00
Saving KERI CESR to hby {
    "v": "KERI10JSON0001b7_",
    "t": "icp",
    "d": "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP",
    "i": "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP",
    "s": "0",
    "kt": "1",
    "k": [
        "DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr"
    ],
    "nt": "1",
    "n": [
        "ELa775aLyane1vdiJEuexP8zrueiIoG995pZPGJiBzGX"
    ],
    "bt": "3",
    "b": [
        "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
        "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
        "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
    ],
    "c": [],
    "a": []
}-VBq-AABAABv33lz0MENsIaM2J1hsbl_8awkJlVT7M1Cnzix0JQSEEwhfSsOt5Wqvuw27wUUKZLCScKoT01FV4WfowFrh_MN-BADAAC_SiZWJFOCuIB_py4gqaMFQtTVWtFCpPfP2LgyqqUS2naTh0nZNlH6MPHSbQNRoImkHnMFrUiBr5ZtwvQ-tNwIABBazaCrt7WQD5Dj1U3KqlZhgOPh7-ca2S0BnRRSEHxW5yoECaC04nyTxYh_wU9TH2WLr14hP-mLHHJDM-wM2esOACA2lyZPmqv2mefIL3orZNm8vb7pyLO5R4zOhHqqXkS1utJrKndiNd4Yu4c6xJnVkc-l6DABB9qe-otLGCkoWDEI-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2024-02-02T14c44c12d081323p00c00
```

## Older example info to remove
### Check if files are available on your server

Note: Replace with your actual web address and AID

https://peacekeeper.github.io/did-webs-iiw37-tutorial/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/did.json

https://peacekeeper.github.io/did-webs-iiw37-tutorial/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/keri.cesr


### (Optional) Resolve AID as did:keri using local resolver

Optionally resolve the AID locally as did:keri, given an OOBI as resolution option.

Note: Replace with your actual AID

```
dkr did keri resolve --name controller --did did:keri:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP --oobi http://witnesshost:5642/oobi/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
```

### (Optional) Resolve AID as did:webs using local resolver

Optionally resolve the AID locally as did:webs.

Note: Replace with your actual web address and AID

```
dkr did webs resolve --name controller --did did:webs:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP
```

### Resolve as did:web using Universal Resolver

https://dev.uniresolver.io/#did:web:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP

### Resolve as did:webs using Universal Resolver

https://dev.uniresolver.io/#did:webs:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP

### Example key rotation

Use the following two commands in your running Docker container.

```
kli rotate --name controller --alias controller
```
Be sure to repeat the `dkr webs generate` command:
```
dkr did webs generate --name controller --did did:webs:blockchainbird.org:did-webs:EG8GsKYdICKs-zI6odM6tvCmxRT2J-7UkZFqA77agtb8 --oobi http://witnesshost:5642/oobi/EG8GsKYdICKs-zI6odM6tvCmxRT2J-7UkZFqA77agtb8/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
```
Now upload the overwritten `did.json` and `keri.cesr` again to the public spot.

### Result

A diff comparison of the old (in green) and the new (in red) **did.json**:
![did.json new in red versus old in green](./images/diff-did-json.png)
A diff comparison of the old (right) and the new (left) **keri.cesr**; in blue the added part:
![keri.cesr new in red versus old in green](./images/diff-keri-cesr.png)

## Trouble shooting

### If you are using an Apple Silicon (M1) mac then you might need to:
* In Docker, select `Use Rosetta for x86/amd64 emulation on Apple Silicon`
* Before running docker compose `export DOCKER_DEFAULT_PLATFORM=linux/amd64`

### Your docker container is already up- and running?

#### Do you have a witness up for another identifier?
Then the `kli incept --name controller --alias controller --file "/keripy/my-scripts/my-incept.json"` command will give this response:

`ERR: Already incepted pre=[Your prefix of another AID].`
 
#### Solution
Various solutions if you're a Docker expert. If not, we'll go down the more rigorous path:

1. Step out of the running container with `exit` 
2. and then `docker compose down`. This should respond with:

[+] Running 3/3
 ⠿ Container dkr                            Removed                                                                                                                                                                              0.0s
 ⠿ Container witnesshost                    Removed                                                                                                                                                                             13.7s
 ⠿ Network did-webs-iiw37-tutorial_default  Removed                                                                                                                                                                              3.1s
Now you could continue with:
```
docker compose up -d
docker compose exec dkr /bin/bash
```
### Special attention Github Pages: web address
There's no problem that we know of when you use Github pages in a bare-bones manner. However, if you use static page generators to populate your github pages (e.g. Jekyll or Docusaurus) be sure to choose the right spot of your files and extract the right paths of the links needed to resolve:

#### Example
This is the web address of the `docusaurus` directory:
https://weboftrust.github.io/WOT-terms/test/did-webs-iiw37-tutorial/

But the exact spot to extract the files as text would be something like:
```
http://raw.githubusercontent.com/WOT-terms/test/did-webs-iiw37-tutorial/[your AID] 
```
The reason for this confusion is that a static page generator like Docusaurus or Jekyll might interfere with the location, visibility and accessibility of your files on Github Pages.

We advise to choose a simple public directory that you control and we won't go into more detail on how to deal with static site generators.

Example:
```
dkr did keri resolve --name dkr --did did:keri:EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6 --oobi http://witnesshost:5642/oobi/EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
```
 
```
        did:keri:123, oobi    ---------------------------------            ---------------------
   O    ----------------->   |                                 |          |                     |
  -|-   <-----------------   |  dkr did keri resolve           |  <---->  |  KERI WATCHER POOL  |
  / \    diddoc, metadata    |                                 |          |                     |
                              ---------------------------------            ---------------------
```

### `dkr did keri resolver-service`

**Expose did:keri resolver as an HTTP web service.** (Can be deployed as Universal Resolver driver)

Example:
```
dkr did keri resolver-service --name dkr --port 7678
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did keri resolver-service  |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                              HTTP GET      ^   |  200 OK
                              did:keri:123  |   |  diddoc
                              oobi          |   v  metadata

                                              o
                                             -|-
                                             / \
```

## did:webs

### `dkr did webs generate`

**Generate a did:webs DID document and KEL/TEL file.**

Example:
```
dkr did webs generate --name dkr --did did:webs:danubetech.com:example:EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6
```

```
                              ---------------------------------
      did.json, keri.cesr    |                                 |
    --------------------->   |  ANY WEB SERVER  /123/did.json  |
   |                         |                  /123/keri.cesr |
   |    UPLOAD                ---------------------------------
   |
   |      
         did:webs:dom:123     ---------------------------------            ---------------------
   O    ----------------->   |                                 |          |                     |
  -|-   <-----------------   |  dkr did webs generate          |  <---->  |  KERI WATCHER POOL  |
  / \   did.json, keri.cesr  |                                 |          |                     |
                              ---------------------------------            ---------------------
```

### `dkr did webs service`

**Launch web server capable of serving KERI AIDs as did:webs and did:web DIDs.**

Example:
```
dkr did webs service --name dkr --port 7676
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

         did:webs:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEBS RESOLVER          |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                                            |   v          

         did:web:dom:123      ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEB RESOLVER           |
  / \         diddoc         |                                 |
                              ---------------------------------
```

### `dkr did webs resolve`

**Resolve a did:webs DID.**

Example:
```
dkr did webs resolve --name dkr --did did:webs:danubetech.com:example:EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

         did:webs:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  dkr did webs resolve           |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```
                              ---------------------------------
                             |                                 |
                             |  ANY WEB SERVER  /123/did.json  |
                             |                  /123/keri.cesr |
                              ---------------------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

         did:webs:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  dkr did webs resolve           |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```
                              ---------------------------------
                             |                                 |
                             |  ANY WEB SERVER  /123/did.json  |
                             |                  /123/keri.cesr |
                              ---------------------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                                            |   v

         did:web:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEB RESOLVER           |
  / \         diddoc         |                                 |
                              ---------------------------------
```

### `dkr did webs resolver-service`

**Expose did:webs resolver as an HTTP web service.** (Can be deployed as Universal Resolver driver)

Example:
```
dkr did keri resolve --name dkr --port 7677
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

                              ---------------------------------
                             |                                 |
                             |  dkr did webs resolver-service  |  <-----  (verify did.json/keri.cesr)
                             |                                 |
                              ---------------------------------
                                            HTTPS
                              HTTP GET      ^   |  200 OK
                              did:webs:123  |   |  diddoc
                              oobi          |   v  metadata

                                              o
                                             -|-
                                             / \
```

```
                              ---------------------------------
                             |                                 |
                             |  ANY WEB SERVER  /123/did.json  |
                             |                  /123/keri.cesr |
                              ---------------------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

                              ---------------------------------
                             |                                 |
                             |  dkr did webs resolver-service  |  <-----  (verify did.json/keri.cesr)
                             |                                 |
                              ---------------------------------
                                            HTTPS
                              HTTP GET      ^   |  200 OK
                              did:webs:123  |   |  diddoc
                                            |   v  metadata

                                              o
                                             -|-
                                             / \
```
