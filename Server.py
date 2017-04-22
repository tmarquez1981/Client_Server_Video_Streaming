# Tom Marquez/Ben Guranious
#
# Server class for video streaming
# Uses RTP to packetize video file
# While server is in playing state, server
# periodically stores a JPEG frame and sends via UDP

import sys
import socket
import random
import pickle
import sys
import os
import filecmp

class Server:
    def __init__(self, listenPort = 33122, debug=False):
        self.port = listenPort
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug = debug
        self.host = ""
        self.sock.bind((self.host, self.port))
        self.currentState = "setup"
        self.destAddress = ""
        self.state = {
            "setup": self.setup,
            "play": self.play,
            "pause": self.pause,
            "teardown": self.teardown
        }

    # receive function
    def receive(self):
        return self.sock.recvfrom(4096)

    def start(self):
        while True:

            try:
                print("Waiting for connection...")

                pickledMsg, self.destAddress = self.receive()
                message = pickle.loads(pickledMsg)

                print("Connection received!")

                while True:
                    self.handleState(self.currentState)

            except (KeyboardInterrupt, SystemExit):
                exit()

    # state handler
    def handleState(self, state):

        if state == "setup":
            setupDone = self.setup()
            if setupDone:
                self.currentState = "play"

    # Handles the setup call from the client
    def setup(self):
        dirName = os.listdir(os.getcwd())
        while True:
            self.send(dirName, self.destAddress) # send list of files in directory to client TODO: Will have to add the encoding
            pickledMsg, self.destAddress = self.receive() # receives filename and if encoding is ok for client
            fileName = pickle.loads(pickledMsg) # checks to see if is in dir. if not, send contents of dir again
            #if ok:
            for file in dirName:
                try:
                    if filecmp.cmp(fileName, file):
                        return True
                except OSError:
                    print('got an error')
                    break
            return False

    # Todo: The following states
    def play(self):
        print("play")

    def pause(self):
        print("pause")

    def teardown(self):
        print("teardown")

    def send(self, packet, address):
        pickledMsg = pickle.dumps(packet)
        self.sock.sendto(pickledMsg, address)

if __name__ == "__main__":
    s = Server()
    s.start()