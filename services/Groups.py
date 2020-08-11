
from services.Encryption import *

def createGroup(text, groups):
    try:
        if not any(d['group'] == text for d in groups): 
            groups.append({"group" : text, "components": []})
            with open("./data/groups.txt", "a") as myfile:
                myfile.write(text)
                myfile.write('\n')
            open("./components/"+text+".txt", 'a').close()
            return True, "Group created successfully."
        else:
            return False, "Group already exist."
    except:
        return False, "Can't create this group."

async def joinGroup(websocket, users, groups, group):
    if any(d['group'] == group for d in groups):
        index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
        users[index]["group"] = group
        groupIndex = next((i for i, item in enumerate(groups) if item["group"] == group), None)
        components = groups[groupIndex]["components"]
        if(len(components) > 0):
            message = {"type" : "components", "value" : components, "success" : True}
            await encrypt_msg(websocket, users[index]["key"], json.dumps(message))
        return True, "Group joined succesfully."
    else:
        return False, "Group doesn't exist."

def leaveGroup(websocket, users, groups, group):
    if any(d['group'] == group for d in groups):
        index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
        if users[index]["group"] == group: 
            users[index]["group"] = None
        return True, "Group leaved succesfully."
    else:
        return False, "Group doesn't exist."
