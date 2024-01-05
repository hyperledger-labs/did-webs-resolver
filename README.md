# Introduction

Welcome to the `did:webs` reference implementation repository. See the did:webs [specification](https://trustoverip.github.io/tswg-did-method-webs-specification/) for more information.

Thank you to Phil Feairheller @pfeairheller from GLEIF who started this work [here](https://github.com/WebOfTrust/did-keri-resolver)

# Developers - Getting Started

Developers who want to jump into using the `did:webs` reference implementation should follow the [Getting Started](./GETTING_STARTED.md) guide.

Thank you to Markus Sabadello @peacekeeper from DanubeTech who started the original tutorial for IIW37 [here](https://github.com/peacekeeper/did-webs-iiw-tutorial)

# dkr

did:keri/did:webs DID Resolver Reference Implementation

* `dkr did keri resolve`
* `dkr did keri resolver-service`
* `dkr did webs generate`
* `dkr did webs service`
* `dkr did webs resolve`
* `dkr did webs resolver-service`

## did:keri

### `dkr did keri resolve`

**Resolve a did:keri DID.**

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
