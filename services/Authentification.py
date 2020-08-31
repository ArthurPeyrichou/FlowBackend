from services.Global import *
from services.Groups import *
import json
import os
appPath = os.path.join('data/')

def getClientIndex(websocket, clients):
    index = next((i for i, item in enumerate(clients) if item["websocket"] == websocket), None)
    if isinstance(index, int) and index >= 0:
        return index
    else :
        return -1

async def wsClientRegister(websocket, clients):
    index = getClientIndex(websocket, clients)
    if index < 0:
        clients.append({ "websocket" : websocket, "group" : None, "key" : None, "isLogin": False, "group": False})
        return True, "Client WS registered succesfully."
    else:
        return False, "Client already registered."

async def wsClientUnregister(websocket, clients):
    index = getClientIndex(websocket, clients)
    if clients[index]:
        clients.pop(index)
        return True, "Client WS unregistered succesfully."
    else:
        return False, "Client doesn't exist."

def register(client, userName, userPassword):
    usersFile = os.path.join(appPath, 'users')
    if os.path.exists(usersFile):
        # Load existing users
        with open(usersFile, 'r') as file:
            data = file.read()
            file.close()
            users = json.loads(data)
            idList = []
            for user in users:
                idList.append(user["id"])
                if user["name"] == userName:
                    return False, "User with this name already registered."
            
            newId = generateId()
            while newId in idList:
                newId = generateId()
            users.append({"id": newId, "name": userName, "password": saltMessage(userPassword)})
            client["isLogin"] = True
            client["name"] = userName
            client["id"] = newId
            with open(usersFile, 'w') as file:
                file.write(json.dumps(users))
                file.close()
                return True, "User registered successfully."
    return False, "User registering failed."


def login(client, userName, userPassword): 
    usersFile = os.path.join(appPath, 'users')
    if os.path.exists(usersFile):
        # Load existing clients
        with open(usersFile, 'r') as file:
            data = file.read()
            file.close()
            users = json.loads(data)
            saltedPassWord = saltMessage(userPassword)
            for user in users:
                if user["name"] == userName:
                    if user["password"] == saltedPassWord:
                        client["isLogin"] = True
                        client["name"] = userName
                        client["id"] = user["id"]
                        res = {"success": False, "msg": ''}
                        res["succes"],res["msg"] = getUserGroup(user["id"])
                        if res["succes"]:
                            client["group"] = json.loads(res["msg"])
                        return True, "User login successfully."
                    else:
                        return False, "Wrong password."
    return False, "User doesn't exist."

def logout(client): 
    client["isLogin"] = False
    client["group"] = False
    client["name"] = ""
    client["id"] = ""
    return True, "User logout successfully."

def setClientKey(client, key):
    client["key"] = key
    return True, "User key set successfully."

def authService(client, msg):
    if "state" in msg:
        if msg["state"] == "key":
            return setClientKey(client, msg["key"])
        elif msg["state"] == "register":
            return register(client, msg["userName"], msg["userPassword"])
        elif msg["state"] == "login":
            return login(client, msg["userName"], msg["userPassword"])
        elif msg["state"] == "logout":
            return logout(client)
    else:
        return False, "Unknown msg, wrong structure."
