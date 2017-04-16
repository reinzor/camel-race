#!/usr/bin/env python

import argparse
import json
import websocket_server


class Server:
    def __init__(self, ip, port):
        self._server = websocket_server.WebsocketServer(port, host=ip)
        self._server.set_fn_message_received(self._incoming_message)

    def _incoming_message(self, client, server, message):
        ip, port = client["address"]
        origin = {
            "ip": ip,
            "port": port
        }

        message = json.loads(message)
        message["origin"] = origin

        print("Broadcasting message", message)

        self._server.send_message_to_all(json.dumps(message))

    def spin(self):
        self._server.run_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camel race client")
    parser.add_argument("--ip", help='Server IP', default='localhost', type=str)
    parser.add_argument("--port", help="Server port", default=3000, type=int)
    args = parser.parse_args()

    s = Server(args.ip, args.port)
    s.spin()
