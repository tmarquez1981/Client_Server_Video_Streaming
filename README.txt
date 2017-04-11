Thomas Marquez Benjamin Gurganious

CSCE A365
Assignment 3 Client/Server Video Streaming

Purpose: To design an client/server application that will stream video files. The client will use RTSP to control
the actions of the server, while the server will use RTP to packetize video for transport to the client.

CLIENT: Client sends SETUP, PLAY, PAUSE, and TEARDOWN commands and the server will respond to the commands. The client
will receive the RTP packet containing JPEG frames, decompress the frames, and render the frames on the client's monitor.

SERVER: While server is in playing state, it will periodically grab a stored JPEG frame and send the frame via
RTP via UDP.