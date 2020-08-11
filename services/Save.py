def saveIntoFile(websocket, users, groups):
    userIndex = next((i for i, item in enumerate(users) if item["websocket"] == websocket), None)
    group = users[userIndex]["group"]
    if any(d['group'] == group for d in groups):
        index = next((i for i, item in enumerate(groups) if item["group"] == group), None)
        text = groups[index]["components"]
        fileName = group + ".txt"
        with open("components/"+fileName, mode='w+', encoding='utf-8') as myfile:
            for lines in text:
                myfile.write((str(lines)))
                myfile.write('\n')
        return True, "Saved changes successfully."
    return False, "Save failed, an error occurred."
    