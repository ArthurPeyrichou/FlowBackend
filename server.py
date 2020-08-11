#!/usr/bin/env python

# WSS (WS over TLS) server example, with a self-signed certificate

import asyncio
import pathlib
import ssl
import websockets
import json
import logging

logging.basicConfig()

USERS = []
COMPONENTS = []
GROUPS = []


async def register(websocket):
    if not any(d['websocket'] == websocket for d in USERS):
        USERS.append({ "websocket" : websocket, "group" : None})
        text = { "type" : "user_count", "value" : len(USERS), "success" : True}
        message = json.dumps(text)
        await asyncio.wait([user["websocket"].send(message) for user in USERS])
        print(type(websocket))
        print(USERS)

async def joinGroup(websocket, group):
    if any(d['group'] == group for d in GROUPS):
        index = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
        USERS[index]["group"] = group
        groupIndex = next((i for i, item in enumerate(GROUPS) if item["group"] == group), None)
        components = GROUPS[groupIndex]["components"]
        if(len(components) > 0):
            message = {"type" : "components", "value" : components, "success" : True}
            print(message)
            await websocket.send(json.dumps(message))
        print(USERS)
        return True
    else:
        return False

def leaveGroup(websocket, group):
    if any(d['group'] == group for d in GROUPS):
        index = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
        if USERS[index]["group"] == group: 
            USERS[index]["group"] = None

def createGroup(text):
    try:
        if not any(d['group'] == text for d in GROUPS): 
            GROUPS.append({"group" : text, "components": []})
            with open("groups.txt", "a") as myfile:
                myfile.write(text)
                myfile.write('\n')
            open("components/"+text+".txt", 'a').close()
            return True
        else:
            return False
    except:
        return False

def setUsername(websocket, username):
    index = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
    USERS[index]["username"] = username
    print(USERS)

async def removeComponent(websocket, index):
    userIndex = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
    group = USERS[userIndex]["group"]
    groupIndex = next((i for i, item in enumerate(GROUPS) if item["group"] == group), None)
    index = int(index)
    if any(d['group'] == group for d in GROUPS):
        if len(GROUPS[groupIndex]["components"]) > index:
            GROUPS[groupIndex]["components"].pop(index)

            components = GROUPS[index]["components"]
            userGroup = next(item for item in USERS if item["group"] == group)
            message = {"type" : "components", "value" : components, "success" : True}
            await asyncio.wait([user["websocket"].send(json.dumps(message)) for user in userGroup])

            return True
        print(GROUPS[groupIndex]["components"])
    return False

async def broadcast(text, websocket):
    if USERS:  # asyncio.wait doesn't accept an empty list
        text = {"type" : "BroadcastFromUser", "value" : text, "From" : str(websocket), "success" : True }
        message = json.dumps(text)
        await asyncio.wait([user["websocket"].send(message) for user in USERS])

def save_to_file(websocket):
    userIndex = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
    print(userIndex)
    group = USERS[userIndex]["group"]
    if any(d['group'] == group for d in GROUPS):
        index = next((i for i, item in enumerate(GROUPS) if item["group"] == group), None)
        text = GROUPS[index]["components"]
        fileName = group + ".txt"
        with open("components/"+fileName, mode='w+', encoding='utf-8') as myfile:
            for lines in text:
                myfile.write((str(lines)))
                myfile.write('\n')
        return True
    return False

async def unregister(websocket):
    index = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
    USERS.pop(index)
    print(USERS)

def checkComponents():
    tmpComponents = []
    with open("groups.txt") as myfile:
        myline = myfile.readline()
        
        while myline:
            myline = myline.rstrip('\n')
            tmpName = myline
            print(myline)
            fileName = myline + ".txt"
            with open("components/"+fileName) as fp:
                line = fp.readline()
                while line:
                    line = line.rstrip('\n')
                    tmpComponents.append(line)
                    line = fp.readline()
            print(tmpName)
            print(tmpComponents)
            GROUPS.append({"group" : tmpName, "components": tmpComponents})
            tmpComponents = []
            myline = myfile.readline()
                    
            

def getComponents(websocket):
    index = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
    group = USERS[index]["group"]
    if any(d['group'] == group for d in GROUPS):
        index = next((i for i, item in enumerate(GROUPS) if item["group"] == group), None)
        return True, GROUPS[index]["components"]
    else:
        return False, "group doesnt exist"
    

async def addComponents(websocket, component):
    index = next((i for i, item in enumerate(USERS) if item["websocket"] == websocket), None)
    group = USERS[index]["group"]
    if group and any(d['group'] == group for d in GROUPS):
        index = next((i for i, item in enumerate(GROUPS) if item["group"] == group), None)
        GROUPS[index]["components"].append(component)
        components = GROUPS[index]["components"]

        userGroup = [item for item in USERS if item["group"] == group]
        if(len(userGroup) == 1):
            userGroup = [userGroup]
        print(userGroup)
        message = {"type" : "components", "value" : components, "success" : True}
        await asyncio.wait([user["websocket"].send(json.dumps(message)) for user in userGroup])
        
        return True
    else:
        return False

async def hello(websocket, path):
    checkComponents()
    while True :
        await register(websocket)
        print(websocket)
        message = await websocket.recv()
        print(message)
        msg = json.loads(message)
        msgType = msg["type"]
        msgValue = msg["value"]
        print(f"< {msgType}")
        print(f"< {msgValue}")
        res = {"type" : msgType, "value": msgValue, "success" : True}

        if msgType == "add":
            ok = await addComponents(websocket, msgValue)
            if not ok :
                res["success"] = False
                res["value"] = "Join a group or create a group or your group doesnt exist anymore"
            print(COMPONENTS)

        elif msgType == "name":
            setUsername(websocket, msgValue)
            
        elif msgType == "remove":
            ok = await removeComponent(websocket, msgValue)
            if not ok:
                res["success"] = False
                res["value"] = "an error occured"

        elif msgType == "save":
            ok = save_to_file(websocket)
            if not ok:
                res["success"] = False
                res["value"]= "an error occured"

        elif msgType == "broadcast":
            

            await broadcast(msgValue, websocket)
        
        elif msgType == "components":
            res["success"], res["value"]= getComponents(websocket)

        elif msgType == "createGroup":
            ok = createGroup(msgValue)
            if ok:
                ok2 = await joinGroup(websocket, msgValue)
            else:
                res["success"] = False
                res["value"] =  "Group already exist"

        elif msgType == "joinGroup":
            ok = await joinGroup(websocket, msgValue)
            if not ok:
                res["success"] = False
                res["value"]= "Group doesnt exist"

        elif msgType == "leaveGroup":
            leaveGroup(websocket, msgValue)

        else :
            res["success"] = False
            res["value"] = "Couldn't process message"
        
        await websocket.send(json.dumps(res))
        print(f"> {res}")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("cert.pem")
ssl_context.load_cert_chain(localhost_pem, keyfile="key.pem")

start_server = websockets.serve(
    hello, "localhost", 8765, ssl=ssl_context
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()