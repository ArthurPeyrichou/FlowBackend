def getUserIndex(websocket, users):
    index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    if index >= 0:
        return index
    else :
        return -1

async def register(websocket, users):
    if not any(user['websocket'] == websocket for user in users):
        users.append({ "websocket" : websocket, "group" : None, "key" : None})
        return True, "User registered succesfully."
    else:
        return False, "User already registered."

def setUserKey(websocket, users, key):
    index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    if users[index] and any(user == users[index]  for user in users):
        users[index]["key"] = key
        return True, "User key set successfully."
    else:
        return False, "User doesn't exist."

def setUsername(websocket, users, username):
    index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    if users[index] and any(user == users[index]  for user in users):
        users[index]["username"] = username
        return True, "Username set successfully."
    else:
        return False, "User doesn't exist."

async def unregister(websocket, users):
    index = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    if users[index] and any(user == users[index]  for user in users):
        users.pop(index)
        return True, "User unregistered succesfully."
    else:
        return False, "User doesn't exist."
