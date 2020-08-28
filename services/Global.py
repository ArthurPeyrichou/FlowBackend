import hashlib, uuid
import random

def generateId(length = 10):
    res = ''
    i = 0
    while (i < length):
        res += f'{random.randint(1, 9)}'
        i +=1
    return res

def generateKey(length = 256):
    res = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    i = 0
    while (i < length):
        res += chars[random.randint(0, len(chars)-1)]
        i +=1
    return res

#TODO
def saltMessage(msg):
    salt = uuid.uuid4().hex
    res = hashlib.sha512(msg.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    return msg
    