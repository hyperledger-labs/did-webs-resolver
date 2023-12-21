# Developers - Getting Started

Welcome to the `did:webs` reference implementation Getting Started guide.

Thank you to Markus Sabadello @peacekeeper from DanubeTech who created the original guide for IIW37 [here](https://github.com/peacekeeper/did-webs-iiw-tutorial)

If you're running into trouble in the process below, be sure to check the section [Trouble Shooting](#trouble-shooting) below. 

Let's get started! We'll use docker to setup and run in a simple environment.

## Run Docker build
```
docker compose build
```

## Run Docker containers for the keri witness network and the `did:webs` generator and resolver environment

```
docker compose down
docker compose up -d
```

## Enter the docker environment command line to begin running keri, etc. commands

```
docker compose exec dkr /bin/bash
```

## Run the script or execute the commands yourself
If you would like to run the script, you can do so by running the following command:

```
cd examples
./get_started_keri.sh "controller" "/keripy/my-scripts" "config-docker" "incept-wits.json"
./get_started_webs.sh "controller" "labs.hyperledger.org:did-webs-resolver:pages" "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP"
```
Otherwise you can type these commands manually.
Lets go through each step.

## (Optional) You can use the KERI-client (kli) to create a unique salt (seed) for your KERI AID private keys

```
kli salt
```

Example response:

```
0AAQmsjh-C7kAJZQEzdrzwB7
```

Note: In our examples we will use this salt `0AAQmsjh-C7kAJZQEzdrzwB7`, if you generated your own then replace it when necessary

## Provide your unique salt and configure your KERI AID

You control this AID so lets call it `controller`.
The config-file in the container is at /keripy/my-scripts/my-config and contains the oobis of the witnesses that we'll use:
In this case they are available from the witness network that we started in the docker-compose. If you `cat` the config at `/keripy/my-scripts/keri/cf/my-config.json` you should see:

`config`
```json
bash-5.1# cat /keripy/my-scripts/keri/cf/my-config.json
{
  "dt": "2022-01-20T12:57:59.823350+00:00",
  "iurls": [
    "http://witnesshost:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller",
    "http://witnesshost:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller",
    "http://witnesshost:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller"
  ]
}
```
Run the init command to prep your environment with the config:
```
kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir "/keripy/my-scripts" --config-file my-config
```

`output`
```
bash-5.1# kli init --name controller --salt 0AAQmsjh-C7kAJZQEzdrzwB7 --nopasscode --config-dir "/keripy/my-scripts" --config-file my-config
KERI Keystore created at: /usr/local/var/keri/ks/controller
KERI Database created at: /usr/local/var/keri/db/controller
KERI Credential Store created at: /usr/local/var/keri/reg/controller

Loading 3 OOBIs...
http://witnesshost:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller succeeded
http://witnesshost:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller succeeded
http://witnesshost:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller succeeded
```

## Create your KERI AID
Now that you have intitalized things, create your AID (via an inception event) with inception configuration that contains your witnesses. It is a transferable AID (meaning you can rotate the keys, witnesses, etc):

`config`
```json
bash-5.1# cat /keripy/my-scripts/my-incept.json
{
  "transferable": true,
  "wits": [
    "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
    "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
    "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
  ]...
}
```

Run the incept command to create your AID:
```
kli incept --name controller --alias controller --file "/keripy/my-scripts/my-incept.json"
```

`output`
```
bash-5.1# kli incept --name controller --alias controller --file "/keripy/my-scripts/my-incept.json"
Waiting for witness receipts...
Prefix  EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP
        Public key 1:  DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr
```

Congrats! You have an AID `EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP` with one public key as the current key `DHr0-I-mMN7h6cLMOTRJkkfPuMd0vgQPrOk4Y3edaHjr`

## (Optional) Perform more KERI operations

Optionally use `kli` to perform additional KERI operations such as key rotation, threshold signatures, etc., see KERI docs for details.

See [a key rotation example](#example-key-rotation) below.


## Decide your web address for did:webs

Find a web address (domain, optional port, optional path) that you control.

Example web address:

```
https://labs.hyperledger.org/did-webs-resolver/pages/
```

## Generate did:webs files for AID

Note: Replace with your actual web address and AID, convert to did:web(s) conformant identifier

Be sure to execute the command in the root of your local `did-webs` repo (and in the Docker container)
```
dkr did webs generate --name controller --did did:webs:labs.hyperledger.org:did-webs-resolver:pages:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP
```

This creates files:
-  `did.json` and `keri.cesr` under local path `./volume/dkr/examples/<your AID>/did.json`

You can access these files either from within your Docker container or on your local computer filesystem.
- `<local path on computer to did-webs-resolver>/volume/dkr/examples/<your AID>` 
- `/usr/local/var/did-keri-resolver/volume/dkr/examples/<your AID>` (local path in the Docker container)


## Upload did.json and keri.cesr to your web server

E.g. using git, Github pages, FTP, SCP, etc.

### Example WOT-terms install using git

We choose `WOT-terms` as our [DESTINATION LOCAL REPO]

```
cd [PATH TO LOCAL SOURCE REPO did-webs-iiw37-tutorial]/volume/dkr/did_json/ENbWS51Pw1rmxz5QIfK5kp3ODaEeQcZjqQNrLpc6mMQq
cp did.json ~/apps/WOT-terms/
cd ../../keri_cesr/ENbWS51Pw1rmxz5QIfK5kp3ODaEeQcZjqQNrLpc6mMQq
cp keri.cesr ~/apps/WOT-terms/
```

Result in local WOT-terms repo
```
[DESTINATION LOCAL REPO]: git status

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	did.json
	keri.cesr

git add .
git commit -m "prepare upload did:webs documents to WOT-terms"  
git push upstream main
```
If you get the expected output of the push action, the files are on the controlled webserver.

## Check if files are available on your server

Note: Replace with your actual web address and AID

https://peacekeeper.github.io/did-webs-iiw37-tutorial/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/did.json

https://peacekeeper.github.io/did-webs-iiw37-tutorial/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/keri.cesr


## (Optional) Resolve AID as did:keri using local resolver

Optionally resolve the AID locally as did:keri, given an OOBI as resolution option.

Note: Replace with your actual AID

```
dkr did keri resolve --name controller --did did:keri:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP --oobi http://witnesshost:5642/oobi/EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
```

## (Optional) Resolve AID as did:webs using local resolver

Optionally resolve the AID locally as did:webs.

Note: Replace with your actual web address and AID

```
dkr did webs resolve --name controller --did did:webs:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP
```

## Resolve as did:web using Universal Resolver

https://dev.uniresolver.io/#did:web:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP

## Resolve as did:webs using Universal Resolver

https://dev.uniresolver.io/#did:webs:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP

## Example key rotation

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
The reason for this confusion is dat a static page generator like Docusaurus or Jekyll might interfere with the location, visibility and accessibility of your files on Github Pages.

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
