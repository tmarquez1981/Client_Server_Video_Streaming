# Tom Marquez/Ben Gurganious
#
# Client for Video streaming
# Uses RTSP to control server
# Requests video from server
# Must implmenet SETUP, PLAY, PAUSE, TEARDDOWN using RTSP

from PIL import Image as img
from PIL import ImageTk
from tkinter import *
import pickle
import socket
from tkinter import messagebox
from tkinter import ttk
import BasicPacket
import threading
import time

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

    def catchAll(self):
        while True:
            try:
                self.s.settimeout(0.5)
                self.s.recvfrom(4096)
            except socket.timeout:
                break

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

        self.paused = False # variable used to interrupt playing

        # some styling
        style = ttk.Style()
        style.configure("TLabel", font="bold")

        # initialize connection object for communicating with server
        self.conn = Connection(destPort, destAddress)

        self.frame = Frame(master, width = windowWidth, height = windowHeight)
        self.frame.pack(fill = "both", expand = "yes")
        self.toolbar = Frame(self.frame, bg = "blue")
        self.setupButton = Button(self.toolbar, text="Setup", command=self.setup, state=NORMAL)
        self.playButton = Button(self.toolbar, text="Play", command=self.play, state=DISABLED)
        self.pauseButton = Button(self.toolbar, text="Pause", command=self.pause, state=DISABLED)
        self.teardownButton = Button(self.toolbar, text="TearDown", command=self.teardown, state=DISABLED)
        self.setupButton.pack(side = LEFT, padx = 1, pady = 2)
        self.playButton.pack(side = LEFT, padx=1, pady=2)
        self.pauseButton.pack(side = LEFT, padx=1, pady=2)
        self.teardownButton.pack(side = LEFT, padx=1, pady=2)
        self.toolbar.pack(side = TOP, fill = X)

        self.frame2 = LabelFrame(self.frame, padx = 2, pady = 2)
        self.frame2.pack(side = BOTTOM, fill = "both", expand = "yes")
        self.mediaLabel = Label(self.frame2)

        self.pb = ttk.Progressbar(self.frame2, orient="horizontal", mode="indeterminate")

        self.progressLabel = Label(self.frame2, text="Progress Bar", relief=SUNKEN, pady=2)

        self.labelPack = []  # an array of dynamic widgets that get set to forget when video is playing

        # random declaration of widget so it can be used in other functions
        self.optionEntry = Entry(self.frame, bd = 2)
        self.labelPack.append(self.optionEntry)

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
        self.labelPack.append(fileLabel)

        for fileName in message:
            self.dirList.append(fileName) # used for error checking of input for file entry
            tempName = StringVar()
            tempName.set(fileName)
            tempButton = Label(self.frame, textvariable = tempName, relief = SUNKEN)
            tempButton.pack(side = TOP, anchor = W)
            self.labelPack.append(tempButton)

        optionLabel = ttk.Label(self.frame, text="Choose a file:")
        optionLabel.pack(side=TOP, anchor=NW)
        self.labelPack.append(optionLabel)
        self.optionEntry.pack(side=TOP, anchor=W)

        okButton = Button(self.frame, text="Click when done", command=self.okButton)
        okButton.pack(side=TOP, anchor=W)
        self.labelPack.append(okButton)

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
                # enable "play", "pause", and "teardown" buttons
                # after valid file is entered and sent to server
                self.playButton["state"] = NORMAL
                self.pauseButton["state"] = NORMAL
                self.teardownButton["state"] = NORMAL

                # the following loops hides the various widgets that are not needed anymore
                for label in self.labelPack:
                    label.pack_forget()

                break
            else:
                found = False
        if not found:
            messagebox.showinfo("Error", "You entered an invalid file name. Please try again")

    # displays image
    def display(self, finalImage):
        self.mediaLabel.config( image = finalImage )
        self.mediaLabel.image=finalImage

    # Performs action after play button is pressed
    # Sends basicPacket
    def play(self):
        # display progress bar and progress label
        self.pb.pack(side=BOTTOM, fill=X)
        self.progressLabel.pack(side=BOTTOM)
        self.pb.start()  # start progress bar

        packet = BasicPacket.BasicPacket("play", self.timestamp)
        packet=packet.makePkt()
        self.conn.send(packet)
        #cv2.namedWindow,tuple(["VIDEO", cv2.WINDOW_FULLSCREEN])

        threading._start_new_thread(self.stream, tuple())
        self.mediaLabel.pack(side=TOP, fill="both", expand="yes")


        print("play")
        #cv2.destroyWindow("VIDEO")

    def stream(self):

        pickledMsg, address = self.conn.receive()
        framerate = pickle.loads(pickledMsg)


        pickledMsg, address = self.conn.receive()
        message = pickle.loads(pickledMsg)
        displayed=False
        frames=[]
        timestamps=[]
        lastframe=""
        while not self.paused and not(message=="END"):
            if message == "FEND":
                pickledMsg, address = self.conn.receive()
                message = pickle.loads(pickledMsg)
            frame=[]
            for i in range(0,message[0]):
                frame.append([])
            pickledMsg, address = self.conn.receive()
            message = pickle.loads(pickledMsg) # message schema = payload(0), seqno(1), timeStamp(2), SSRC(3), video frame(4)

            while not(message=="END" or message=="FEND") and len(message)>2 and not(self.paused):
                self.seqno = message[0][1]
                self.ssrc = message[0][3]
                frame[int(message[1])] = message[2]
                timestamps.append(message[0][2])
                pickledMsg, address = self.conn.receive()
                message = pickle.loads(pickledMsg)
            if not(lastframe=="") and self.containsBlank(frame):
                lastframe=self.stitch(frame,lastframe)
                frames.append(self.convertToPhotoImage(lastframe))
            else:
                lastframe = frame
                frames.append(self.convertToPhotoImage(lastframe))
            if(len(frames)>10) and not displayed:
                threading._start_new_thread(self.displaythread,tuple([frames, timestamps, framerate]))
                displayed = True

        self.conn.catchAll()
        if not displayed:
            threading._start_new_thread(self.displaythread, tuple([frames, timestamps, framerate]))
            displayed = True

    def stitch(self, one, two):
        for i in range(0, len(one)):
            if one[i]==[]:
                one[i]=two[i]
        return one

    def containsBlank(self, array):
        for i in range(0, len(array)):
            if array[i]==[]:
                return True
        return False

    def convertToPhotoImage(self, data):
        myImage = img.new("RGB",(len(data[0]),len(data)))
        for y in range(0,len(data)):
            for x in range(0, len(data[y])):
                myImage.putpixel((x,y),tuple(data[y][x]))
        finalImage = ImageTk.PhotoImage(myImage)
        return finalImage

    #function to be called from another thread; displays frames 1 at a time according to framerate
    def displaythread(self, frames, timestamps, framerate):
        while not self.paused:
            if len(frames)>0:
                frame = frames[0]
                frames.remove(frame)
                timestamp=timestamps[0]
                timestamps.remove(timestamp)
                self.timestamp=timestamp
                self.display(frame)
                time.sleep(framerate)


    def pause(self):
        self.pause=True
        packet = BasicPacket.BasicPacket("pause", self.timestamp)
        packet=packet.makePkt()
        self.conn.send(packet)
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