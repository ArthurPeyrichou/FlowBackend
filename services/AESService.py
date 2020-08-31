from base64 import b64decode, b64encode, b16encode, b16decode
from Crypto.Random import get_random_bytes
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util import Counter
import binascii
import hashlib
import logging
import random
import json

def aes_ocb_decrypt(key, ciphertext):
    if key != None:
        try:
            b64 = json.loads(ciphertext)
            json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
            jv = {k:b64decode(b64[k]) for k in json_k}
            cipher = AES.new(key, AES.MODE_OCB, nonce=jv['nonce'])
            cipher.update(jv['header'])
            res =  cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
            return res.decode('utf-8')
        except:
            logging.error("Incorrect decryption")
    return ''

def aes_ocb_encrypt(key, plaintext):
    if key != None:
        header = b"header"
        data = plaintext.encode('utf-8')
        cipher = AES.new(key, AES.MODE_OCB)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
        json_v = [ b64encode(x).decode('utf-8') for x in (cipher.nonce, header, ciphertext, tag) ]
        return json.dumps(dict(zip(json_k, json_v)))
    return ''

def aes_ctr_decrypt(key, cipher):
    if key != None:
        try:
            b64 = json.loads(cipher)
            nonce = b64decode(b64['nonce'])
            ct = b64decode(b64['ciphertext'])
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            res = cipher.decrypt(ct)
            return res.decode('utf-8')
        except Exception as ex:
            logging.error(ex)
    return ''

def aes_ctr_encrypt(key, plaintext):
    if key != None:
        iv = aes_genIv()
        iv_int = int(binascii.hexlify(iv), 16)
        ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
        cipher = AES.new(key, AES.MODE_CTR, counter=ctr)

        data = plaintext.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CTR)
        ct_bytes = cipher.encrypt(data)
        nonce = b64encode(cipher.nonce).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')
        return json.dumps({'nonce':nonce, 'ciphertext':ct})
    return ''

def aes_ctr_decrypt_2 (key, iv, cyphertext): 
    if key != None and iv != None:
        key = hashlib.sha256(key).digest()
        iv_int = int(b16encode(iv), 16)
        logging.error(key)
        logging.error(iv_int)
        logging.error(b64decode(cyphertext.encode('utf-8')))
        ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
        cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
        return cipher.decrypt(b64decode(cyphertext.encode('utf-8'))).decode('utf-8')
    return ''

def aes_ctr_encrypt_2 (key, iv, plainText):
    if key != None and iv != None:
        key = hashlib.sha256(key).digest()
        iv_int = int(b16encode(iv), 16)
        ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
        cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
        res = cipher.encrypt(plainText.encode('utf-8'))
        return b64encode(res).decode('utf-8')
    return ''

def aes_genKey(length = 32):
    return get_random_bytes(length)

def aes_genIv():
    return Random.new().read(AES.block_size)
