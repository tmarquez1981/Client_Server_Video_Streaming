# Tom Marquez/Ben Gurganious
#
# Server class for video streaming
# Uses RTP to packetize video file
# While server is in playing state, server
# periodically stores a JPEG frame and sends via UDP

import socket
import random
import pickle
import os
import cv2
import time

import RTP_Packet
import threading

# Thread class
# Listen for interrupts from client
class myThread (threading.Thread):
    def __init__(self, mainhandle):
        threading.Thread.__init__(self)
        self.mainhandle=mainhandle

    def run(self):
        print("Starting thread")
        self.mainhandle.listening()

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
        self.paused = False # variable used to interrupt streaming
        self.first=True
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
                    if done:
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
            self.pause(self.timestamp)
            return True

        if state == "teardown":
            self.teardown()
            return False


    # Handles the setup call from the client
    def setup(self):
        dirName = os.listdir(os.getcwd())
        self.send(dirName, self.destAddress) # send list of files in directory to client
        pickledMsg, self.destAddress = self.receive() # receives filename
        fileName = pickle.loads(pickledMsg)
        self.file = fileName
        self.currentState = "play"

    # Play function is the video streaming function
    # It should loop through and continuously stream until either EOF
    # or interrupted by client
    def play(self):

        # The listening thread
        thread = myThread(self)
        thread.start()

        # TODO: Theoretically, this should stream a video file
        # and stop at an interrupt from the client
        # Note: this has not been tested and more than likely needs some work.
        # I believe video frames need to be converted to byte arrays
        # for processing on the client side
        cap = cv2.VideoCapture()
        cap.open(self.file)
        framerate = (10.0/float(cap.get(cv2.CAP_PROP_FPS)))
        self.send(framerate,self.destAddress)
        while not self.paused:
            # opens video file
            ret, frame = cap.read()
            if frame == None:
                break
            timeStamp = cap.get(cv2.CAP_PROP_POS_MSEC) # returns current timestamp in video
            if self.first:
                self.first=False
                self.timestamp=timeStamp
            if(timeStamp>=self.timestamp):
                self.send_rows(frame,timeStamp, framerate)

        print("play")

    def send_rows(self, data, timestamp, framerate):
        self.send( [ len(data), len(data[0]) ] , self.destAddress)
        sleeprate = (framerate/float(len(data)))/100.0
        for rown in range(0, len(data)):
            rtpPacket = RTP_Packet.RTP_Packet("MJPG", self.seqn, timestamp, self.ssrc)
            rtpPacket = rtpPacket.makeRTP_Pkt()
            finalPacket = rtpPacket , rown , data[rown]
            self.send(finalPacket,self.destAddress)
        print("sent a frame")
        self.send("FEND", self.destAddress)


    # function that will be spawned off a thread to listen for streaming interrupts from client
    def listening(self):
        pickledMsg, self.destAddress = self.receive()
        message = pickle.loads(pickledMsg) # message scheme = msgType, timestamp
        msgType = message[0]
        timeStamp = message[1]
        if msgType == "pause":
            self.pause(timeStamp)
            return

    def pause(self, timeStamp):
        self.paused = True
        self.timestamp=timeStamp #will begin sending from time paused
        print("pause")

    def teardown(self):
        print("teardown")

    def send(self, packet, address):
        pickledMsg = pickle.dumps(packet)
        self.sock.sendto(pickledMsg, address)

if __name__ == "__main__":
    s = Server()
    s.start()

