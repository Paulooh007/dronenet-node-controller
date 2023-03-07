myIPAddress = "192.168.10.1"
myIPAddress = "192.168.0.119"    #WIFI 2

ffmpegProcessId = 1000000
nodeControllerIPAddress = "192.168.43.179"

# controlCenterIPAddress = "192.168.137.1"
# controlCenterIPAddress = "192.168.0.156"
controlCenterIPAddress = "192.168.0.108"

telloIPAddress = "0.0.0.0"
commandCenterPort = 33333
nodeControllerPort = 22222

telloVideoSourcePort = 11111
localVideoStreamPort = 4000
remoteVideoStreamPort = 5000

classList = ["person","car","motorbike", "bus"]

telloCommand = "ffmpeg -probesize 32 -analyzeduration 0 -i udp://"\
            + str(telloIPAddress) + ":" \
            + str(telloVideoSourcePort) \
            + " -b 300k -minrate 200k -maxrate 400k -bufsize 600k -f mpegts udp://127.0.0.1:" \
            + str(localVideoStreamPort) \
            + "?pkt_size=188&buffer_size=10000&max_delay=1000 -f mpegts udp://" \
            + controlCenterIPAddress + ":" \
            + str(remoteVideoStreamPort) \
            + "?pkt_size=188&buffer_size=10000&max_delay=1000"