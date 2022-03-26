from hashlib import sha512
from Crypto.PublicKey import RSA

def encrypt(hash, key):
    return pow(hash, key.d, key.n)

def decrypt(hash, key):
    return pow(hash, key.e, key.n)

def ecp_sign(message, cert):
    message_hash = int.from_bytes(sha512(message).digest(), byteorder='big')
    key = RSA.import_key(cert)
    signature = encrypt(message_hash, key)
    return hex(signature)

def ecp_verify(message, signature, cert):
    message_hash = int.from_bytes(sha512(message).digest(), byteorder='big')
    key = RSA.import_key(cert)
    decrypted_hash =  decrypt(signature, key)
    return {"valid": message_hash==decrypted_hash, "hash": hex(message_hash), "shash": hex(decrypted_hash)}
