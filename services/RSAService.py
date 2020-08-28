from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

rsa_receiving_key = RSA.importKey(open("keys/rsa_2048_priv.pem", "rb").read())
cipher_receiving = PKCS1_v1_5.new(rsa_receiving_key)

def rsa_decrypt(cryptedMsg):
    h = cryptedMsg.split(',')
    res = ''
    i = 0
    while i < len(h):
        res += cipher_receiving.decrypt(b64decode(h[i]), Random.new().read(256)).decode("utf-8")
        i += 1  
    return res

def rsa_encrypt(key, msg):
    if key != None:
        rsa_sending_key = RSA.importKey(key)
        cipher_sending = PKCS1_v1_5.new(rsa_sending_key)

        inBytes = msg.encode('utf-8')
        msg_len = len(inBytes)
        # key size / 8 - 11 (-1 for security)
        max_len = 110
        if msg_len <= max_len:
            res = cipher_sending.encrypt(inBytes)
            return b64encode(res).decode('utf-8')
        else :
            offset = 0
            res = ''
            while offset < msg_len:
                size = min(max_len, msg_len - offset)
                if (offset + size - msg_len) == 0:
                    res += b64encode(cipher_sending.encrypt(inBytes[-size:])).decode("utf-8")
                else: 
                    res += b64encode(cipher_sending.encrypt(inBytes[offset:offset + size - msg_len])).decode("utf-8")
                    res += ','
                offset += size
            return res
    return ''
