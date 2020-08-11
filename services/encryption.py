from Crypto.Cipher import AES, PKCS1_OAEP
from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

rsa_receiving_key = RSA.importKey(open("keys/rsa_2048_priv.pem", "rb").read())
cipher_receiving = PKCS1_v1_5.new(rsa_receiving_key)

def decrypt_msg(cryptedMsg):
    h = cryptedMsg.split(',')
    res = ''
    i = 0
    while i < len(h):
        res += cipher_receiving.decrypt(b64decode(h[i]), Random.new().read(256)).decode("utf-8")
        i += 1  
    return res

async def encrypt_msg(websocket, key, msg):
    if key != None:
        rsa_sending_key = RSA.importKey(key)
        cipher_sending = PKCS1_v1_5.new(rsa_sending_key)

        msg_len = len(msg)
        if msg_len <= 100:
            res = cipher_sending.encrypt(msg.encode('utf-8'))
            await websocket.send(b64encode(res).decode('utf-8'))
        else :
            offset = 0
            res =''
            while offset < msg_len:
                size = min(100, msg_len - offset)
                if (offset + size - msg_len) == 0:
                    res += b64encode(cipher_sending.encrypt(msg[-size:].encode('utf-8'))).decode("utf-8")
                else: 
                    res += b64encode(cipher_sending.encrypt(msg[offset:offset + size - msg_len].encode('utf-8'))).decode("utf-8")
                    res += ','
                offset += size
            await websocket.send(res)