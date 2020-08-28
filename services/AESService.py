from base64 import b64decode, b64encode
from Crypto.Cipher import AES
import random

def aes_decrypt(key, cryptedMsg):
    if key != None:
        cipher = AES.new(key, AES.MODE_EAX)
        return cipher.decrypt(cryptedMsg)
    return ''

def aes_encrypt(key, msg):
    if key != None:
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(msg)     
        return ciphertext
    return ''
