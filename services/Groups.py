
from services.Global import *
import json
import os

appPath = os.path.join('data/')
groupsFile = os.path.join(appPath, 'groups')
membersFile = os.path.join(appPath, 'members')
usersFile = os.path.join(appPath, 'users')
invitationsFile = os.path.join(appPath, 'invition')

def createGroup(groupName, client):
    if os.path.exists(groupsFile):
        # Load existing groups
        with open(groupsFile, 'r') as file:
            data = file.read()
            file.close()
            groups = json.loads(data)
            idList = []
            for group in groups:
                idList.append(group["id"])
                if group["name"] == groupName:
                    return False, "A group with this name already exist."
            
            newId = generateId()
            while newId in idList:
                newId = generateId()
            groups.append({"id": newId, "name": groupName})
            
            res = {"msg": '', "success": False}
            res["success"],res["msg"] = createMember(newId, client['id'], 'leader')
            if res["success"]:
                with open(groupsFile, 'w') as file:
                    file.write(json.dumps(groups))
                    file.close()
                client['group'] = {"id": newId, "name": groupName}
            return res["success"], "Group created succesfully. You are the leader of this group."
    return False, "Group creation failed."

#It does not check if the userId and the groupId exist
def createInvitationInGroup(userId, groupId):
    if os.path.exists(invitationsFile):
        # Load existing invitations
        with open(invitationsFile, 'r') as file:
            data = file.read()
            file.close()
            invitations = json.loads(data)
            idList = []
            for invitation in invitations:
                idList.append(invitation["id"])
                if invitation["group"] == groupId and invitation["user"] == userId:
                    return False, "A invitation from this group to this user already exist."
            
            newId = generateId()
            while newId in idList:
                newId = generateId()
            invitations.append({"id": newId, "group": groupId, "user": userId})
            with open(invitationsFile, 'w') as file:
                file.write(json.dumps(invitations))
                file.close()
                return True, "invitation created successfully."
    return False, "invitation creation failed."

def createMember(groupId, userId, status = 'guest'):
    if os.path.exists(membersFile):
        # Load existing members
        with open(membersFile, 'r') as file:
            data = file.read()
            file.close()
            members = json.loads(data)
            idList = []
            for member in members:
                idList.append(member["id"])
                if member["user"] == userId:
                    return False, "You are already member of a group."
            
            newId = generateId()
            while newId in idList:
                newId = generateId()
            members.append({"id": newId, "group": groupId, "user": userId, "status": status})
            with open(membersFile, 'w') as file:
                file.write(json.dumps(members))
                file.close()
                return True, "Member created successfully."
    return False, "Member creation failed."

#It does not warn other member that he's joining the group
def acceptInvitAndJoinGroup(invitationId):
    res = {"msg": '', "success": False}
    if os.path.exists(invitationsFile):
        # Load existing invitation
        with open(invitationsFile, 'r') as file:
            data = file.read()
            file.close()
            invitations = json.loads(data)
            saltedPassWord = saltMessage(userPassword)
            for invitation in invitations:
                if invitation["id"] == invitationId:
                    res["success"],res["msg"] = createMember(invitation["group"], invitation["user"])
                    if res["success"]:
                        invitations.pop(invitation)
                        for invitToDrop in invitations:
                            if invitToDrop["user"] == invitation["user"]:
                                invitations.pop(invitToDrop)
                    return res["success"], "Group joined succesfully. You are a guest of this group."
   
    return False, "Invitation doesn't exist."

#It does not warn other member that he's declining the invitation
def declineInvitInGroup(invitationId):
    res = {"msg": '', "success": False}
    if os.path.exists(invitationsFile):
        # Load existing invitation
        with open(invitationsFile, 'r') as file:
            data = file.read()
            file.close()
            invitations = json.loads(data)
            saltedPassWord = saltMessage(userPassword)
            for invitation in invitations:
                if invitation["id"] == invitationId:
                    invitations.pop(invitation)
                    return res["success"], "Group invitation declined succesfully."
   
    return False, "Invitation doesn't exist."

#It does not warn other member that he's leaving the group
def leaveGroup(client):
    if os.path.exists(membersFile):
        # Load existing members
        with open(membersFile, 'r') as file:
            data = file.read()
            file.close()
            members = json.loads(data)
            for member in members:
                if member["user"] == client['id']:
                    members.pop(member)
                    with open(membersFile, 'w') as file:
                        file.write(json.dumps(members))
                        file.close()
                        client['group'] = False
                        return True, "Group leaved successfully."  
            return False, "You are not member of a group."
    return False, "Group leaving failed."

#It does not check who ask for group deletion
def deleteGroup(groupId):
    if os.path.exists(groupsFile) and os.path.exists(membersFile) and os.path.exists(invitationsFile):
        # Load existing groups
        with open(groupsFile, 'r') as file:
            data = file.read()
            file.close()
            groups = json.loads(data)
            for group in groups:
                if groups["id"] == groupId:
                    groups.pop(group)
                    with open(membersFile, 'w') as file:
                        file.write(json.dumps(groups))
                        file.close()
                        # Load existing members
                        with open(membersFile, 'r') as file:
                            data = file.read()
                            file.close()
                            members = json.loads(data)
                            for member in members:
                                if member["group"] == groupId:
                                    members.pop(member)
                            with open(membersFile, 'w') as file:
                                file.write(json.dumps(members))
                                file.close()
                        # Load existing invitations
                        with open(invitationsFile, 'r') as file:
                            data = file.read()
                            file.close()
                            invitations = json.loads(data)
                            for invitation in invitations:
                                if invitation["group"] == groupId:
                                    invitations.pop(invitation)
                            with open(invitationsFile, 'w') as file:
                                file.write(json.dumps(invitations))
                                file.close()

                        return True, "Group deleted successfully."  
            return False, "This group does not exist."
    return False, "Group deletion failed."

def getUserGroup(userId):
    if os.path.exists(groupsFile) and os.path.exists(membersFile):
        # Load existing members
        with open(membersFile, 'r') as file:
            data = file.read()
            file.close()
            members = json.loads(data)
            for member in members:
                if member["user"] == userId:
                    # Load existing groups
                    with open(groupsFile, 'r') as file:
                        data = file.read()
                        file.close()
                        groups = json.loads(data) 
                        for group in groups:
                            if group['id'] == member["group"]:
                                return True, json.dumps({'groupId': member["group"], 'groupName': group['name'], 'status': member["status"]})
                        return False, "No group with the given identifiant find."
            return False, "This user have no group."

    return False, "Group recovery failed."

def getUserInvitations(userId):
    if os.path.exists(groupsFile) and os.path.exists(invitationsFile):
        # Load existing groups
        with open(groupsFile, 'r') as file:
            data = file.read()
            file.close()
            groups = json.loads(data)
            # Load existing members
            with open(invitationsFile, 'r') as file:
                data = file.read()
                file.close()
                invitations = json.loads(data)
                userinvitations = []
                for invitation in invitations:
                    if invitation['user'] == userId:
                        for group in groups:
                            if group['id'] == invitation['group']:
                                userinvitations.append({'id': invitation['id'], 'groupId': invitation['group'], 'groupName': group['name']})
                return True, json.dumps(userinvitations)
    return False, "User's invitations recovery failed."

def getGroupMembers(groupId):
    if os.path.exists(usersFile) and os.path.exists(membersFile):
        # Load existing users
        with open(usersFile, 'r') as file:
            data = file.read()
            file.close()
            users = json.loads(data)
            # Load existing members
            with open(membersFile, 'r') as file:
                data = file.read()
                file.close()
                members = json.loads(data)
                groupMembers = []
                for member in members:
                    if member['group'] == groupId:
                        for user in users:
                            if user['id'] == member['user']:
                                groupMembers.append({'id': member['user'], 'name': user['name'], 'status': member['status']})
                return True, json.dumps(groupMembers)
    return False, "Group's members recovery failed."

def groupService(websocket, client, msg):
    if "state" in msg:
        if msg["state"] == "create":
            return createGroup( msg["groupName"], client)
        elif msg["state"] == "invite":
            return createInvitationInGroup(msg["userId"], client["group"]["id"])
        elif msg["state"] == "join":
            return acceptInvitAndJoinGroup(msg["invitationId"])
        elif msg["state"] == "decline":
            return declineInvitInGroup(msg["invitationId"])
        elif msg["state"] == "leave":
            return leaveGroup(client)
        elif msg["state"] == "invitations":
            return getUserInvitations(client["id"])
        elif msg["state"] == "members":
            return getGroupMembers(client["group"]["id"])
    else:
        return False, "Unknown msg, wrong structure."
