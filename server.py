#!/usr/bin/env python

import logging
import json
from websocket_server import WebsocketServer

    
def incoming_message(client, server, message):
    ip, port = client["address"]
    origin = {
        "ip": ip,
        "port": port
    }
    
    message = json.loads(message)
    message["origin"] = origin
    
    print("Broadcasting message", message)
    
    server.send_message_to_all(json.dumps(message))

server = WebsocketServer(3000, host='127.0.0.1', loglevel=logging.INFO)
server.set_fn_message_received(incoming_message)
server.run_forever()
