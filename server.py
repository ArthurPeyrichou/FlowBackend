#!/usr/bin/env python
# WSS (WS over TLS) server example, with a self-signed certificate
from LoggerFormater import (LoggerFormatter, loggingWebsocket)
from Flow import Flow
from services.Authentification import *
from services.Encryption import *
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
        await asyncio.wait([encrypt_msg(user["websocket"], user["key"], json.dumps(message)) for user in CLIENTS])

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
            myJson = json.loads(decrypt_msg(cryptedMsg))
            #If the websocket message is in many parts
            if "msg" in myJson:
                if myJson["msg"] == "start":
                    recvdMsg = myJson["body"]
                elif myJson["msg"] == "middle":
                    recvdMsg += myJson["body"]
                elif myJson["msg"] == "end":
                    recvdMsg += myJson["body"]  
                    recvdMsg = json.loads(recvdMsg)
            else :
                recvdMsg = myJson

            #If the websocket message is complet
            if isinstance(recvdMsg, str) == False:
                logging.info(f"\n   - Received: {recvdMsg}")
                if "type" in recvdMsg:
                    if recvdMsg["type"] == "auth":
                        res = {"type" : recvdMsg["type"], "body": {"state": recvdMsg["body"]["state"], "msg": "Couldn't process message", "success" : False}}
                        res["body"]["success"], res["body"]["msg"] = authService(websocket, CLIENTS[index], recvdMsg["body"]) 
                        await encrypt_msg(websocket, CLIENTS[index]["key"], json.dumps(res))
                        logging.info(f"\033[32m   - Responded {res}")
                        
                        if recvdMsg["body"]["state"] in ["login", "register"] and CLIENTS[index]["isLogin"] and FLOW is not None: 
                            await FLOW.onConnect()
                    elif CLIENTS[index]['isLogin'] and FLOW is not None: 
                        await FLOW.onMessage(recvdMsg)
                elif CLIENTS[index]['isLogin'] and FLOW is not None: 
                        await FLOW.onMessage(recvdMsg)

            '''elif isinstance(recvdMsg, str) == False
                logging.warning(f"\n   - Wrong format (ignores), received: {recvdMsg}")'''
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

    logging.info("---     Running server on localhost:8765     ---")
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(main, 'localhost', 8765, ssl=ssl_context))
    logging.info('--- Server listening, press any key to abort ---\n')
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt as error:
    logging.warning('\n--- Keyboard pressed  ---')
    logging.warning('---   Server closed   ---\n')
