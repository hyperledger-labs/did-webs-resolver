from keri.core import eventing, coring

from didcomm.common.types import DID, VerificationMethodType, VerificationMaterial, VerificationMaterialFormat
from didcomm.common.resolvers import SecretsResolver
from didcomm.did_doc.did_doc import DIDDoc, VerificationMethod, DIDCommService
from didcomm.did_doc.did_resolver import DIDResolver
from didcomm.secrets.secrets_resolver_demo import  Secret


from typing import Optional, List
import pysodium
import base64
import json
from pprint import pp


'''
Utilities for DIDComm packing and unpacking using did:keri as alternative to Peer DID
- Use SICPA didcomm-python library
- Authcryypt message only
- AID is Ed25519 and derive X25519 key pair from same private key
- Transferable AID but with no next key that makes it non transferable (no key rotations)
'''

def createKeriDid():
    salt = coring.Salter()
    signerEd25519 = salt.signer(transferable=True, temp=True)

    X25519_pubkey = pysodium.crypto_sign_pk_to_box_pk(signerEd25519.verfer.raw)
    # Manual CESR coding
    X25519_pubkey_qb64 = 'C'+ (base64.urlsafe_b64encode(bytes([0]) + X25519_pubkey).decode('utf-8'))[1:]
    # Or using karipy
    X25519_pubkey_qb64 = coring.Matter(raw = X25519_pubkey, code=coring.MtrDex.X25519).qb64

    serder = eventing.incept(
        keys=[signerEd25519.verfer.qb64], 
        data=[
                {"e":X25519_pubkey_qb64},
                {"se": "https://example.coom/"}
            ], 
        code=coring.MtrDex.Blake3_256 # code is for self-addressing
    )

    did = 'did:keri:'+serder.ked['i']
    kelb64 = base64.urlsafe_b64encode(bytes(json.dumps(serder.ked), 'utf-8')).decode('utf-8')
    long_did = did+'?icp='+kelb64

    # pp(serder.ked)

    return {
        'did': did,
        'long_did': long_did,
        'signer': signerEd25519
    }

def validateLongDid(long_did):
    # TODO validate URL and make parsing safer
    did = long_did.split('?')[0]
    kelb64 = long_did.split('=')[1]+"=="
    kel_decoded = json.loads(base64.urlsafe_b64decode(kelb64))
    prefixer = coring.Prefixer(ked=kel_decoded)
    return prefixer.qb64b.decode("utf-8") == did.split(':')[2]

class SecretsResolverInMemory(SecretsResolver):
    def __init__(self, store: dict):
        self._store = store

    async def get_key(self, kid: str) -> Optional[Secret]:
        
        did, kident = kid.split('#')

        signer = self._store[did]['signer']
        X25519_pubkey = pysodium.crypto_sign_pk_to_box_pk(signer.verfer.raw)
        X25519_pubkey_b64 = base64.urlsafe_b64encode(X25519_pubkey).decode('utf-8')
        X25519_prikey = pysodium.crypto_sign_sk_to_box_sk(signer.raw + signer.verfer.raw)
        X25519_prikey_b64 = base64.urlsafe_b64encode(X25519_prikey).decode('utf-8')

        Ed25519_pubkey_raw = signer.verfer.raw
        Ed25519_pubkey_b64 = base64.urlsafe_b64encode(Ed25519_pubkey_raw).decode('utf-8')
        
        Ed25519_prikey_raw = signer.raw
        Ed25519_prikey_b64 = base64.urlsafe_b64encode(Ed25519_prikey_raw).decode('utf-8')

        secret = Secret(
                kid= kid,
                type= VerificationMethodType.JSON_WEB_KEY_2020,
                verification_material= VerificationMaterial(
                    format=VerificationMaterialFormat.JWK,
                    value= json.dumps(
                        {
                            'kty': 'OKP',
                            'crv': 'X25519',
                            'd': X25519_prikey_b64,
                            'x': X25519_pubkey_b64,
                            'kid': kid
                        } if kident == "key-1" else 
                        {
                            'kty': 'OKP',
                            'crv': 'Ed25519',
                            'd': Ed25519_prikey_b64,
                            'x': Ed25519_pubkey_b64,
                            'kid': kid
                        }
                    )
                )
        )        
        return secret

    async def get_keys(self, kids: List[str]) -> List[str]:
        return kids

class DidKeriResolver(DIDResolver):
    def __init__(self, store: dict):
        self._store = store
    async def resolve(self, did: DID) -> DIDDoc:
        # TODO validate URL and make parsing safer
        short_did = did.split('?')[0]
        if len(did.split('=')) > 1:  
            kelb64 = did.split('=')[1]+"=="
            ked = json.loads(base64.urlsafe_b64decode(kelb64))
            self._store[short_did]['ked'] = ked
        else:
            ked = self._store[short_did]['ked']

        # Manual CESR Decoding
        ed25519_pubkey_qb64 = ked['k'][0]
        ed25519_pubkey_b64 = "A" + ed25519_pubkey_qb64[1:]
        ed25519_pubkey_raw = base64.urlsafe_b64decode(ed25519_pubkey_b64)[1:]
        x1 = base64.urlsafe_b64encode(ed25519_pubkey_raw).decode('utf-8')
        # Or using keripy:
        x1 = base64.urlsafe_b64encode(coring.Matter(qb64=ked['k'][0]).raw).decode('utf-8')

        x2 = base64.urlsafe_b64encode(coring.Matter(qb64=ked['a'][0]['e']).raw).decode('utf-8')

        return DIDDoc(
            did=did,
            key_agreement_kids = [short_did+'#key-1'],
            authentication_kids = [short_did+'#key-2'],
            verification_methods = [
                VerificationMethod(
                    id = short_did+'#key-1',
                    type = VerificationMethodType.JSON_WEB_KEY_2020,
                    controller = did,
                    verification_material = VerificationMaterial(
                        format = VerificationMaterialFormat.JWK,
                        value = json.dumps({
                                    'kty': 'OKP',
                                    'crv': 'X25519',
                                    'x': x2
                                })
                    )
                ),
                VerificationMethod(
                        id = short_did+'#key-2',
                        type = VerificationMethodType.JSON_WEB_KEY_2020,
                        controller = did,
                        verification_material = VerificationMaterial(
                            format = VerificationMaterialFormat.JWK,
                            value = json.dumps({
                                        'kty': 'OKP',
                                        'crv': 'Ed25519',
                                        'x': x1
                                    })
                        )
                    )    
            ],
            didcomm_services = [
                DIDCommService(
                    id='endpoint-1',
                    service_endpoint=ked['a'][1]['se'],
                    routing_keys=[],
                    accept=["didcomm/v2"]
                )
            ]
        )