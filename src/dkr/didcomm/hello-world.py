from utils import createKeriDid, SecretsResolverInMemory, DidKeriResolver, validateLongDid
from didcomm.message import Message
from didcomm.unpack import unpack
from didcomm.common.resolvers import ResolversConfig
from didcomm.pack_encrypted import pack_encrypted, PackEncryptedConfig
import asyncio
import json

alice = createKeriDid()
print("Alice's DID:", alice['did'])
print("Alice's Long DID:", alice['long_did'],"\n")

bob = createKeriDid()
print("Bob's DID:", bob['did'])
print("Bob's Long DID:", bob['long_did'],"\n")

print("Compare length with Peer DID: did:peer:2.Vz6MkfiT7uT2EQnuNhGP2xxNsh2v7seoV3fzZWRpydJnF3K6z.Ez6LSfpsWUKP7g4LGTpXFPWZzThQtG1VuQqxtToKYtkXdRdc8.SeyJpZCI6IiNzZXJ2aWNlLTEiLCJ0IjoiZG0iLCJzIjoiZGlkOnBlZXI6Mi5FejZMU2U3U3FCUmJmWEdFNXJpVEZYYU5zZ2dWUFB6YThtNXdyR21ON0dRY0d5dHI2LlZ6Nk1ra3dmNWhWcUJVYXhFU3YxVHhra0pIQWNKRldnTXROY1g2Q1pyRkZpZllNQTkuU2V5SnBaQ0k2SW01bGR5MXBaQ0lzSW5RaU9pSmtiU0lzSW5NaU9pSm9kSFJ3Y3pvdkwyMWxaR2xoZEc5eUxuSnZiM1J6YVdRdVkyeHZkV1FpTENKaElqcGJJbVJwWkdOdmJXMHZkaklpWFgwIn","\n")

print("Alice's long DID validation:", validateLongDid(alice['long_did']))
print("Bob's long DID validation:", validateLongDid(bob['long_did']),"\n")

store = {
    alice['did']: alice,
    bob['did']: bob
}

secrets_resolver = SecretsResolverInMemory(store)
did_resolver = DidKeriResolver(store)

# Alice creates a basic message
alice_message =  Message(
    id = "123",
    type = "https://didcomm.org/basicmessage/2.0/message",
    body = {'content': 'Hello Bob!'},
)
print('1-Alice creates a basic message:',alice_message.body,"\n")

# Alice encrypts the message for Bob
alice_message_packed = asyncio.run( pack_encrypted(
    resolvers_config = ResolversConfig(
        secrets_resolver = secrets_resolver,
        did_resolver = did_resolver
    ),
    message = alice_message,
    frm = alice['long_did'],
    to = bob['long_did'],
    sign_frm = None,
    pack_config = PackEncryptedConfig(protect_sender_id=False)
))
print('2-Alice encrypts the message for Bob:')
print(alice_message_packed.packed_msg,"\n")

# Bob decrypts the message
bob_message_unpacked = asyncio.run( unpack(
    resolvers_config=ResolversConfig(
        secrets_resolver=secrets_resolver,
        did_resolver=did_resolver
    ),
    packed_msg= alice_message_packed.packed_msg
))
print('3-Bob decrypts the message:', bob_message_unpacked.message.body,"\n")

# Bob creates a basic message response
bob_message =  Message(
    id = "124",
    type = "https://didcomm.org/basicmessage/2.0/message",
    body = {'content': 'Hello Alice!'},
)
print('4-Bob creates a response using short DIDs:',bob_message.body,"\n")

# Bob encrypts the message for Alice
bob_message_packed = asyncio.run( pack_encrypted(
    resolvers_config = ResolversConfig(
        secrets_resolver = secrets_resolver,
        did_resolver = did_resolver
    ),
    message = bob_message,
    frm = bob['did'],
    to = alice['did'],
    sign_frm = bob['did'],
    pack_config = PackEncryptedConfig(protect_sender_id=False)
))
print('5-Bob encrypts and sign the message for Alice:')
print(bob_message_packed.packed_msg,"\n")

# Alice decrypts the message
alice_message_unpacked = asyncio.run( unpack(
    resolvers_config=ResolversConfig(
        secrets_resolver=secrets_resolver,
        did_resolver=did_resolver
    ),
    packed_msg= bob_message_packed.packed_msg
))
print('6-Alice decrypts the message with short DIDs:', alice_message_unpacked.message.body,"\n")

print(asyncio.run(did_resolver.resolve(alice['did'])))
