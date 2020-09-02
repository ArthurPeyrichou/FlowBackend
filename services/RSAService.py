from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
import urllib.parse
import math

keySize = 4096
maxTextLength = math.ceil(keySize / 8) - 15
rsa_receiving_key = RSA.importKey(open("keys/rsa_4096_priv.pem", "rb").read())
cipher_receiving = PKCS1_v1_5.new(rsa_receiving_key)
isSecurityActive = False

def rsa_decrypt(cryptedMsg):
    if not isSecurityActive: 
        return urllib.parse.unquote(cryptedMsg)
    h = cryptedMsg.split(',')
    res = ''
    i = 0
    while i < len(h):
        res += cipher_receiving.decrypt(b64decode(h[i]), Random.new().read(256)).decode("utf-8")
        i += 1
    return res

def rsa_encrypt(key, msg):
    if not isSecurityActive: 
        return urllib.parse.quote(msg)
    if key != None:
        rsa_sending_key = RSA.importKey(key)
        cipher_sending = PKCS1_v1_5.new(rsa_sending_key)

        inBytes = msg.encode('utf-8')
        msg_len = len(inBytes)
        if msg_len <= maxTextLength:
            res = cipher_sending.encrypt(inBytes)
            return b64encode(res).decode('utf-8')
        else :
            offset = 0
            res = ''
            while offset < msg_len:
                size = min(maxTextLength, msg_len - offset)
                if (offset + size - msg_len) == 0:
                    res += b64encode(cipher_sending.encrypt(inBytes[-size:])).decode("utf-8")
                else: 
                    res += b64encode(cipher_sending.encrypt(inBytes[offset:offset + size - msg_len])).decode("utf-8")
                    res += ','
                offset += size
            return res
    return ''
