# RTP_Packet class defines the packet header for the RTP packet
# Packet is create as a tuple of the following fields:
#   payloadType | seqno | timestamp | SSRC(synchronization source ID)

class RTP_Packet:
    def __init__(self, payload, seqno, timeStamp, SSRC):
        self.payloadType = payload
        self.seqno = seqno
        self.timeStamp = timeStamp
        self.SSRC = SSRC

    # creates an RTP header
    # header: payloadType | seqno | timeStamp | SSRC
    # needs to be appended to a data field
    def makeRTP_Pkt(self):
        packet = self.payloadType, self.seqno, self.timeStamp, self.SSRC
        return packet