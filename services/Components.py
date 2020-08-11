from services.Encryption import *
import asyncio

async def addComponents(websocket, users, groups, component):
    index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    group = users[index]["group"]
    if group and any(g['group'] == group for g in groups):
        index = next((i for i, item in enumerate(groups) if item["group"] == group), None)
        groups[index]["components"].append(component)
        components = groups[index]["components"]

        userGroup = [item for item in users if item["group"] == group]
        if(len(userGroup) == 1):
            userGroup = [userGroup]
        message = {"type" : "components", "value" : components, "success" : True}
        await asyncio.wait([encrypt_msg(user["websocket"], user["key"], json.dumps(message)) for user in userGroup])
        
        return True, "Component added succesfully."
    else:
        return False, "Group already exist."

def checkComponents(groups):
    tmpComponents = []
    with open("./data/groups.txt") as myfile:
        myline = myfile.readline()
        
        while myline:
            myline = myline.rstrip('\n')
            tmpName = myline
            fileName = myline + ".txt"
            with open("./components/"+fileName) as fp:
                line = fp.readline()
                while line:
                    line = line.rstrip('\n')
                    tmpComponents.append(line)
                    line = fp.readline()
            groups.append({"group" : tmpName, "components": tmpComponents})
            tmpComponents = []
            myline = myfile.readline()

def getComponents(websocket, users, groups):
    index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    group = users[index]["group"]
    if any(g['group'] == group for g in groups):
        index = next((i for i, item in enumerate(groups) if item["group"] == group), None)
        return True, json.dumps(groups[index]["components"])
    else:
        return False, "Group doesn't exist."

async def removeComponent(websocket, users, groups, index):
    userIndex = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    group = users[userIndex]["group"]
    groupIndex = next((i for i, item in enumerate(groups) if item["group"] == group), None)
    index = int(index)
    if any(g['group'] == group for g in groups):
        if len(groups[groupIndex]["components"]) > index:
            groups[groupIndex]["components"].pop(index)

            components = groups[index]["components"]
            userGroup = next(item for item in users if item["group"] == group)
            message = {"type" : "components", "value" : components, "success" : True}
            await asyncio.wait([encrypt_msg(user["websocket"], user["key"], json.dumps(message)) for user in userGroup])

            return True, "Component removed succesfully."
    else:
        return False, "Group doesn't exist."
