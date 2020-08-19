import json
import os
import logging
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
        clients.append({ "websocket" : websocket, "group" : None, "key" : None, "isLogin": False})
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
    userMatch = False
    clientsFile = os.path.join(appPath, 'users')
    if os.path.exists(clientsFile):
        # Load existing clients
        with open(clientsFile, 'r') as file:
            data = file.read()
            file.close()
            users = json.loads(data)
            for user in users:
                if user["name"] == userName:
                    return False, "User with this name already registered."
            users.append({"name": userName, "password": userPassword})
            client["isLogin"] = True
            client["name"] = userName
            with open(clientsFile, 'w') as file:
                file.write(json.dumps(users))
                file.close()
                return True, "User registered successfully."
    return False, "User registering failed."


def login(client, userName, userPassword): 
    clientsFile = os.path.join(appPath, 'users')
    if os.path.exists(clientsFile):
        # Load existing clients
        with open(clientsFile, 'r') as file:
            data = file.read()
            file.close()
            users = json.loads(data)
            for user in users:
                logging.info(f"   - !!!! {user}")
                if user["name"] == userName:
                    if user["password"] == userPassword:
                        client["isLogin"] = True
                        client["name"] = userName
                        return True, "User login successfully."
                    else:
                        return False, "Wrong password."
    return False, "User doesn't exist."

def setClientKey(client, key):
    client["key"] = key
    return True, "User key set successfully."

def authService(websocket, client, msg):
    if "state" in msg:
        if msg["state"] == "key":
            return setClientKey(client, msg["key"])
        if msg["state"] == "register":
            return register(client, msg["userName"], msg["userPassword"])
        if msg["state"] == "login":
            return login(client, msg["userName"], msg["userPassword"])
    else:
        return False, "Unknown msg, wrong structure."
