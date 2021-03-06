#!/usr/bin/env python
# WSS (WS over TLS) server example, with a self-signed certificate
from LoggerFormater import (LoggerFormatter, loggingWebsocket)
from Flow import Flow
from services.Authentification import *
from services.RSAService import *
from services.Groups import *
from services.Save import *
import websockets
import traceback
import argparse
import pathlib
import logging
import asyncio
import json
import ssl
import sys

CLIENTS = []
FLOWS = []

async def broadcast(message, websocket):
    if CLIENTS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([user["websocket"].send(rsa_encrypt(user["key"], json.dumps(message))) for user in CLIENTS])

async def main(websocket, path):
    #This part register the client if not registered yet. If new client, broadcast new client count
    res = {"body": "", "success" : False}
    res["success"], res["body"] = await wsClientRegister(websocket, CLIENTS)

    try:
        if res["success"] == True:
            index = getClientIndex(websocket, CLIENTS)
            FLOWS.append(Flow(CLIENTS[index]))
            logging.info(f"   - Registered a new client {websocket}")
            message = { "type" : "online", "body" : len(CLIENTS), "success" : True}
            await broadcast(message, websocket)

        async for cryptedMsg in websocket:
            #Receive a new message crypted
            recvdMsg = json.loads(rsa_decrypt(cryptedMsg))
            logging.info(f"\n   - Received: {recvdMsg}")

            #If the user is not login yet
            if not CLIENTS[index]['isLogin']:
        
                if "type" in recvdMsg and recvdMsg["type"] == "auth":
                    res = getMsgStructure(recvdMsg["type"], recvdMsg["body"]["state"], "Couldn't process message")
                    res["body"]["success"], res["body"]["msg"] = authService(CLIENTS[index], recvdMsg["body"]) 
                    await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                    logging.info(f"\033[32m   - Responded {res}")
                    
                    #If the user is just logged, send him his eventual group and invitations and run Flow
                    if recvdMsg["body"]["state"] in ["login", "register"] and CLIENTS[index]["isLogin"]:
                        res = getMsgStructure("group", "get", "Couldn't process message")
                        res["body"]["success"], res["body"]["msg"] = groupService(CLIENTS[index], {'state': 'get'}) 
                        await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                        logging.info(f"\033[32m   - Send {res}")

                        res = getMsgStructure("group", "invitations", "Couldn't process message")
                        res["body"]["success"], res["body"]["msg"] =  groupService(CLIENTS[index], {'state': 'invitations'}) 
                        await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                        logging.info(f"\033[32m   - Send {res}")

                        #If the user is part of a group
                        logging.warning(CLIENTS[index]["group"])
                        if CLIENTS[index]["group"] is not False:
                            await FLOWS[index].onConnect()
            #The user have been login
            else:
                #The user asking for logout
                if "type" in recvdMsg and recvdMsg["type"] == "auth":
                    if recvdMsg["body"]["state"] == "logout":
                        await FLOWS[index].onClose()
                        res = getMsgStructure(recvdMsg["type"], recvdMsg["body"]["state"], "Couldn't process message")
                        res["body"]["success"], res["body"]["msg"] = authService(CLIENTS[index], recvdMsg["body"]) 
                        await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                        logging.info(f"\033[32m   - Responded {res}")
                #group management
                elif "type" in recvdMsg and recvdMsg["type"] == "group":  
                    res = getMsgStructure(recvdMsg["type"], recvdMsg["body"]["state"], "Couldn't process message")
                    res["body"]["success"], res["body"]["msg"] = groupService(CLIENTS[index], recvdMsg["body"]) 

                    #If the user create or join a group
                    if (recvdMsg["body"]["state"] == "create" or recvdMsg["body"]["state"] == "join") and res["body"]["success"] is True:
                        res["body"]["group"] = recvdMsg["body"]["group"]
                        if CLIENTS[index]["group"] is not False:
                            await FLOWS[index].onConnect()

                    await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                    logging.info(f"\033[32m   - Responded {res}")

                    #If the user delete or leave a group
                    if recvdMsg["body"]["state"] == "leave" and res["body"]["success"] is True:
                        if CLIENTS[index]["group"] is False:
                            await FLOWS[index].onClose()

                    res = getMsgStructure("group", "get", "Couldn't process message")
                    res["body"]["success"], res["body"]["msg"] = groupService(CLIENTS[index], {'state': 'get'}) 
                    await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                    logging.info(f"\033[32m   - Send {res}")

                    res = getMsgStructure("group", "invitations", "Couldn't process message")
                    res["body"]["success"], res["body"]["msg"] =  groupService(CLIENTS[index], {'state': 'invitations'}) 
                    await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                    logging.info(f"\033[32m   - Send {res}")
                #flow management
                else:
                    await FLOWS[index].onMessage(recvdMsg)

    except Exception:
        logging.error(f" Exception occured: {traceback.format_exc()}")

        if CLIENTS[index]["group"] is not False:
            await FLOWS[index].onClose()
        res["success"], res["body"] =  await wsClientUnregister(websocket, CLIENTS)
        if res["success"] == True:
            FLOWS.pop(index)
            index = getClientIndex(websocket, CLIENTS)
            logging.info(f"   - One client leaved server: {websocket}")
            message = { "type" : "online", "body" : len(CLIENTS), "success" : True}
            await broadcast(message, websocket)

try:
    # Configuring arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-wss', '--websocketssl', help='Run server in ssl communication', action='store_true')
    parser.add_argument('-c', '--crypto', help='Run server with encrypt and decrypt communication', action='store_true')
    args = parser.parse_args()

    # Configuring logging for output in terminal
    fmt = LoggerFormatter()
    myHandler = logging.StreamHandler(sys.stdout)
    myHandler.setFormatter(fmt)
    logging.root.addHandler(myHandler)
    logging.root.setLevel(logging.INFO)

    if args.crypto:
        isSecurityActive = True
        logging.info("---     Secure message with RSA crypting activated     ---")
        logging.warn("!!     Be sure to activate security in client side     !!")

    # Configuring ssl certificat for wss
    if args.websocketssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain('keys/ssl-cert.pem', 'keys/ssl-key.pem')

    if args.websocketssl:
        logging.info("---     Running server on wss:5001     ---")
        asyncio.get_event_loop().run_until_complete(websockets.serve(main, '0.0.0.0', 5001, ssl=ssl_context))
    else :
        logging.info("---     Running server on ws:5001     ---")
        asyncio.get_event_loop().run_until_complete(websockets.serve(main, '0.0.0.0', 5001))
    logging.info('--- Server listening, press any key to abort ---\n')

    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt as error:
    logging.warning('\n--- Keyboard pressed  ---')
    logging.warning('---   Server closed   ---\n')
