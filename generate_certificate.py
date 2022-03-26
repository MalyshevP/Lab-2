# генерация нового публичного и приватного ключей

from Crypto.PublicKey import RSA

key = RSA.generate(1024)

f = open('private.pem','wb')
f.write(key.export_key('PEM'))
f.close()

f = open('public.pub','wb')
f.write(key.public_key().export_key('PEM'))
f.close()
