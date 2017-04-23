# Tom Marquez/Ben Gurganious
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
import cv2
import RTP_Packet
import threading

# Thread class
# Listen for interrupts from client
class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting thread")
        Server.listening()

class Server:
    def __init__(self, listenPort = 33122, debug=False):
        self.port = listenPort
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug = debug
        self.host = ""
        self.sock.bind((self.host, self.port))
        self.currentState = "setup"
        self.destAddress = ""
        self.file = ""
        self.ssrc = random.randint(0, 100)
        self.seqn = 0
        self.pause = False # variable used to interrupt streaming
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
                    done = self.handleState(self.currentState)
                    if not done:
                        break

            except (KeyboardInterrupt, SystemExit):
                exit()

    # state handler
    def handleState(self, state):

        if state == "setup":
            self.setup()
            return True

        if state == "play":
            self.play()
            return True

        if state == "pause":
            self.pause()
            return True

        if state == "teardown":
            self.teardown()
            return False


    # Handles the setup call from the client
    def setup(self):
        dirName = os.listdir(os.getcwd())
        self.send(dirName, self.destAddress) # send list of files in directory to client TODO: Will have to add the encoding
        pickledMsg, self.destAddress = self.receive() # receives filename and if encoding is ok for client
        fileName = pickle.loads(pickledMsg)
        #todo: need to implement tag for encoding (maybe?)
        #if ok:

        self.file = fileName
        self.currentState = "play"

    # Play function is the video streaming function
    # It should loop through and continuously stream until either EOF
    # or interrupted by client
    def play(self):

        # The listening thread
        thread = myThread()
        thread.start()

        # TODO: Theoretically, this should stream a video file
        # and stop at an interrupt from the client
        # Note: this has not been tested and more than likely needs some work.
        # I believe video frames need to be converted to byte arrays
        # for processing on the client side
        while not self.pause:
            # opens video file
            cap = cv2.VideoCapture(self.file)
            ret, frame = cap.read()
            timeStamp = cap.get(cv2.CAP_PROP_MSEC) # returns current timestamp in video
            payload = "MJPG"
            rtpPacket = RTP_Packet(payload, self.segn, timeStamp, self.ssrc)
            rtpPacket.makeRTP_Packet()
            completePacket = rtpPacket, frame # send RTP packet and video frame
            self.send(completePacket, self.destAddress)

        print("play")


     # function that will be spawned off a thread to listen for streaming interrupts from client
    def listening(self):
        pickledMsg, self.destAddress = self.receive()
        message = pickle.loads(pickledMsg) # message scheme = msgType, timestamp
        msgType = message[0]
        timeStamp = message[1]
        if msgType == "pause":
            self.pause = True
            return

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