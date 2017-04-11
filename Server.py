# Tom Marquez/Ben Guranious
#
# Server class for video streaming
# Uses RTP to packetize video file
# While server is in playing state, server
# periodically stores a JPEG frame and sends via UDP

import sys
import socket
import random

class Server:
    def __init__(self, listenPort = 33122, debug=False):
        self.port = listenPort
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind('', self.port)
        self.debug = debug
        self.destAddress = ""

    # receive function
    def receive(self):
        return self.sock.recvfrom(4096)

    def start(self):
        while True:
            try:
                message, self.destAddress = self.receive()


            except (KeyboardInterrupt, SystemExit):
                exit()