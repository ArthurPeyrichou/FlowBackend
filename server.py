#!/usr/bin/env python
# WSS (WS over TLS) server example, with a self-signed certificate
from LoggerFormater import (LoggerFormatter, loggingWebsocket)
from Flow import Flow
from services.Authentification import *
from services.Components import *
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

USERS = []
COMPONENTS = []
GROUPS = []
FLOW = None

async def broadcast(message, websocket):
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([encrypt_msg(user["websocket"], user["key"], json.dumps(message)) for user in USERS])

async def main(websocket, path):
    #This part register the client if not registered yet. If new client, broadcast new client count
    
    res = {"body": "", "success" : False}
    res["success"], res["body"] = await register(websocket, USERS)
    if res["success"] == True:
        index = getUserIndex(websocket, USERS)
        if index > -1:
            FLOW = Flow(websocket, USERS[index])
        logging.info(f"   - Registered a new client {websocket}")
        message = { "type" : "online", "body" : len(USERS), "success" : True}
        await broadcast(message, websocket)
    
    checkComponents(GROUPS)


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
            if "type" in recvdMsg and recvdMsg["type"] == "key":
                res = {"type" : recvdMsg["type"], "body": "Couldn't process message", "success" : False}
                res["success"], res["body"] = setUserKey(websocket, USERS, recvdMsg["body"]) 
                await encrypt_msg(websocket, USERS[index]["key"], json.dumps(res))
                logging.info(f"\033[32m   - Responded {res}")
                if FLOW is not None: 
                    await FLOW.onConnect()
            elif FLOW is not None: 
                await FLOW.onMessage(recvdMsg)

        '''elif isinstance(recvdMsg, str) == False
            logging.warning(f"\n   - Wrong format (ignores), received: {recvdMsg}")'''

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
