#!/usr/bin/env python
# WSS (WS over TLS) server example, with a self-signed certificate
from LoggerFormater import (LoggerFormatter, loggingWebsocket)
from Flow import Flow
from services.Authentification import *
from services.RSAService import *
from services.Groups import *
from services.Save import *
import websockets
import pathlib
import logging
import asyncio
import json
import ssl
import sys

CLIENTS = []
FLOW = None

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
            if index > -1:
                FLOW = Flow(websocket, CLIENTS[index])
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

                        if FLOW is not None: 
                            await FLOW.onConnect()
            #The user have been login
            else:
                #The user asking for logout
                if "type" in recvdMsg and recvdMsg["type"] == "auth":
                    if recvdMsg["body"]["state"] == "logout":
                        await FLOW.onClose()
                        res = getMsgStructure(recvdMsg["type"], recvdMsg["body"]["state"], "Couldn't process message")
                        res["body"]["success"], res["body"]["msg"] = authService(CLIENTS[index], recvdMsg["body"]) 
                        await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                        logging.info(f"\033[32m   - Responded {res}")
                #group management
                elif "type" in recvdMsg and recvdMsg["type"] == "group":  
                    res = getMsgStructure(recvdMsg["type"], recvdMsg["body"]["state"], "Couldn't process message")
                    res["body"]["success"], res["body"]["msg"] = groupService(CLIENTS[index], recvdMsg["body"]) 

                    await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                    logging.info(f"\033[32m   - Responded {res}")

                    res = getMsgStructure("group", "get", "Couldn't process message")
                    res["body"]["success"], res["body"]["msg"] = groupService(CLIENTS[index], {'state': 'get'}) 
                    await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                    logging.info(f"\033[32m   - Send {res}")

                    res = getMsgStructure("group", "invitations", "Couldn't process message")
                    res["body"]["success"], res["body"]["msg"] =  groupService(CLIENTS[index], {'state': 'invitations'}) 
                    await websocket.send(rsa_encrypt(CLIENTS[index]["key"], json.dumps(res)))
                    logging.info(f"\033[32m   - Send {res}")
                #flow management
                elif FLOW is not None: 
                        await FLOW.onMessage(recvdMsg)

    finally:
        res["success"], res["body"] =  await wsClientUnregister(websocket, CLIENTS)
        if res["success"] == True:
            index = getClientIndex(websocket, CLIENTS)
            if index > -1:
                FLOW = Flow(websocket, CLIENTS[index])
            logging.info(f"   - One client leaved server: {websocket}")
            message = { "type" : "online", "body" : len(CLIENTS), "success" : True}
            await broadcast(message, websocket)


try:
    # Configuring logging for output in terminal
    fmt = LoggerFormatter()
    myHandler = logging.StreamHandler(sys.stdout)
    myHandler.setFormatter(fmt)
    logging.root.addHandler(myHandler)
    logging.root.setLevel(logging.INFO)

    # Configuring ssl certificat for wss
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('keys/ssl-cert.pem', 'keys/ssl-key.pem')

    logging.info("---     Running server on localhost:5001     ---")
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(main, '0.0.0.0', 5001, ssl=ssl_context))
    logging.info('--- Server listening, press any key to abort ---\n')
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt as error:
    logging.warning('\n--- Keyboard pressed  ---')
    logging.warning('---   Server closed   ---\n')
