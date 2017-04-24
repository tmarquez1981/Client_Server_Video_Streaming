# Tom Marquez/Ben Gurganious
#
# Client for Video streaming
# Uses RTSP to control server
# Requests video from server
# Must implmenet SETUP, PLAY, PAUSE, TEARDDOWN using RTSP

import numpy as np
import cv2
from PIL import Image as img
from PIL import ImageTk
from tkinter import *
import tkinter as tk
import pickle
import socket
import getopt
import sys
from tkinter import messagebox
from tkinter import ttk
import BasicPacket
import threading

windowWidth = 600
windowHeight = 600

# Creates a connection class
class Connection:
    def __init__(self, destPort, destAddress, listeningPort = 30000, debug=False):
        self.debug = debug
        self.host = ""
        self.destPort = destPort
        self.destAddress = destAddress
        self.listeningPort = listeningPort
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.listeningPort))

    # send function sends a message
    def send(self, message, address = None):
        if address is None:
            address = (self.destAddress, self.destPort)
        pickledMsg = pickle.dumps(message)
        self.s.sendto(pickledMsg, address)

    def receive(self):
        return self.s.recvfrom(4096)

# The application class sets the windown and the widgets
class Application:
    def __init__(self, master, destPort, destAddress):

        # holds list of files in the server directory for error checking
        self.dirList = []

        # initialize variables for RTP packet values from server
        self.timestamp = 0
        self.seqno = 0
        self.ssrc = 0 # this may not be needed. It would be nice to ensure server was sending to the right client
                      # but it is really not needed given the scope of this project.

        self.pause = False # variable used to interrupt playing

        # some styling
        style = ttk.Style()
        style.configure("TLabel", font="bold")

        # initialize connection object for communicating with server
        self.conn = Connection(destPort, destAddress)

        self.frame = Frame(master, width = windowWidth, height = windowHeight)
        self.frame.pack(fill = "both", expand = "yes")
        self.toolbar = Frame(self.frame, bg = "blue")
        self.setupButton = Button(self.toolbar, text = "Setup", command = self.setup)
        self.playButton = Button(self.toolbar, text = "Play", command = self.play)
        self.pauseButton = Button(self.toolbar, text = "Pause", command = self.pause)
        self.teardownButton = Button(self.toolbar, text  ="TearDown", command = self.teardown)
        self.setupButton.pack(side = LEFT, padx = 1, pady = 2)
        self.playButton.pack(side = LEFT, padx=1, pady=2)
        self.pauseButton.pack(side = LEFT, padx=1, pady=2)
        self.teardownButton.pack(side = LEFT, padx=1, pady=2)
        self.toolbar.pack(side = TOP, fill = X)

        self.frame2 = LabelFrame(self.frame, padx = 2, pady = 2)
        self.frame2.pack(side = BOTTOM, fill = "both", expand = "yes")
        self.mediaLabel = Label(self.frame2)

        # Todo: Need to change this variable as the status changes
        # Todo: Should display the current state of the video
        # Note: Can use progressbar here instead
        self.statusBarText = StringVar()
        self.statusBarText.set("Status bar...")

        self.statusBar = Frame(self.frame2)
        self.statusLabel = Label(self.statusBar, fg="green", textvariable = self.statusBarText, relief = SUNKEN, anchor = W)
        self.statusLabel.pack(fill = X)
        self.statusBar.pack(side = BOTTOM, fill = X)

        # random declaration of widget so it can be used in other functions
        self.optionEntry = Entry(self.frame, bd = 2)

    # The setup function gets the wheels turning with the server
    # It displays the files in the servers directory
    # It produces labels for each file that is displayed in the window
    # It asks for a file
    # If file entered is invalid, a messagebox is displayed prompting user to re-enter the file
    # If file is valid, it displays it in the window
    # TODO: At the moment, it only displays images.
    def setup(self):
        self.conn.send("Setup")
        pickledMsg, address = self.conn.receive()
        message = pickle.loads(pickledMsg)

        fileLabel = ttk.Label(self.frame, text="List of files:")
        fileLabel.pack(side=TOP, anchor=NW)

        for fileName in message:
            self.dirList.append(fileName) # used for error checking of input for file entry
            tempName = StringVar()
            tempName.set(fileName)
            tempButton = Label(self.frame, textvariable = tempName, relief = SUNKEN)
            tempButton.pack(side = TOP, anchor = W)

        optionLabel = ttk.Label(self.frame, text="Choose a file:")
        optionLabel.pack(side=TOP, anchor=NW)
        # optionEntry = Entry(self.frame, bd = 2)
        self.optionEntry.pack(side=TOP, anchor=W)
        okButton = Button(self.frame, text="Click when done", command=self.okButton)
        okButton.pack(side=TOP, anchor=W)

    # okButton checks to see if file name entered is valid
    # If it is valid, call display()
    # if not valid, display error messagebox
    def okButton(self):
        fileEntered = self.optionEntry.get()
        found = True

        # checks for valid file name entry
        # sends file option to server if name entry is valid
        for fileName in self.dirList:
            if fileEntered == fileName:
                self.conn.send(fileEntered) # sends the name of the chosen file to be streamed
                found = True
                self.path = fileName
                break
            else:
                found = False
        if not found:
            messagebox.showinfo("Error", "You entered an invalid file name. Please try again")

    # displays image
    # should receive a byte array and display
    # TODO: function should have a an argument
    # from this array, a photoImage should be created
    # Currently,
    def display(self, data):
        myImage = img.new("RGB",(len(data[0]),len(data)))
        for y in range(0,len(data)):
            for x in range(0, len(data[y])):
                myImage.putpixel((x,y),tuple(data[y][x]))
        finalImage = ImageTk.PhotoImage(myImage)
        self.mediaLabel.config( image = finalImage )
        self.mediaLabel.image=finalImage
        self.mediaLabel.pack(side=TOP, fill="both", expand="yes")

    # Performs action after play button is pressed
    # Sends basicPacket
    # Todo: the following functions
    def play(self):
        packet = BasicPacket.BasicPacket("play", self.timestamp)
        packet=packet.makePkt()
        self.conn.send(packet)
        #cv2.namedWindow,tuple(["VIDEO", cv2.WINDOW_FULLSCREEN])

        # TODO: Given the fact that I can not get video files to work, this will have to be tested
        # This should loop until at least a frame is done processing
        # Currently, it (theoretically) loops until pause is called, regardless if the frame is done processing or not. 
        threading._start_new_thread(self.stream, tuple())


        print("play")
        #cv2.destroyWindow("VIDEO")

    def stream(self):
        pickledMsg, address = self.conn.receive()
        message = pickle.loads(pickledMsg)
        displayed=False
        while not self.pause:
            if message == "FEND":
                pickledMsg, address = self.conn.receive()
                message = pickle.loads(pickledMsg)
            frame=[]
            for i in range(0,message[0]):
                frame.append([])
            pickledMsg, address = self.conn.receive()
            message = pickle.loads(pickledMsg) # message schema = payload(0), seqno(1), timeStamp(2), SSRC(3), video frame(4)
            while not( message == "FEND") and len(message)>2:
                self.seqno = message[0][1]
                self.timestamp = message[0][2]
                self.ssrc = message[0][3]
                frame[int(message[1])] = message[2]
                pickledMsg, address = self.conn.receive()
                message = pickle.loads(pickledMsg)
            #threading._start_new_thread(self.display,tuple([frame]))
            threading._start_new_thread(self.display,tuple([frame]))


    def pause(self):
        print("pause")

    def teardown(self):
        print("teardown")

# hardcoded the address and port number
destAddress = "127.0.0.1"
destPort = 33122


root = Tk()
root.wm_title("Video")

app = Application(root, destPort, destAddress)


root.mainloop()