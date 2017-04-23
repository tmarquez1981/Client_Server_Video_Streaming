# Class for a basic packet.
# This class could be used for the client packet
# Used when playing and pausing
# BasicPacket schema = messageType, currentTimeStamp
# messageType = either "play" or "pause"
# currentTimeStamp = the timestamp of the video last received by the client

class BasicPacket:
    def __init__(self, messageType, currentTimeStamp):
        self.messageType = messageType
        self.currentTimeStamp = currentTimeStamp

    def makePkt(self):
        packet = self.messageType, self.currentTimeStamp
        return packet
