import numpy as np
import cv2
from cv2 import aruco
from time import sleep
import atexit
from djitellopy import tello
import os
import signal
import subprocess
import socket
from threading import Thread

import keyPressModule as kp
import time

import config

myIPAddress = config.myIPAddress   #WIFI 2

ffmpegProcessId = config.ffmpegProcessId
nodeControllerIPAddress = config.nodeControllerIPAddress
controlCenterIPAddress = config.controlCenterIPAddress

telloIPAddress = config.telloIPAddress
commandCenterPort = config.commandCenterPort
nodeControllerPort = config.nodeControllerIPAddress
telloVideoSourcePort = config.telloVideoSourcePort
localVideoStreamPort = config.localVideoStreamPort
remoteVideoStreamPort = config.remoteVideoStreamPort

UDPDataAvailable = False
UDPData = ""
informControlCenter = False


whT = 320
confThreshold = 0.3
nmsThreshold = 0.2
#### LOAD MODEL
classList = config.classList
classNames = open('coco.names').read().strip().split('\n')
## Model Files
modelConfiguration = "yolov3-tiny.cfg"
modelWeights = "yolov3-tiny.weights"

# modelConfiguration = "yolov3.cfg"
# modelWeights = "yolov3.weights"
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

objectToFind = None

w, h = 1000, 680
# w, h = 500, 300
land = False

telloCommand = config.telloCommand

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((myIPAddress, nodeControllerPort))

from utils_node import getKeyboardIinputNode, alertCommandCenter, monitorUDP, findObjects

def exitRoutine():
    print("Killing all process")
    print("will now try to kill ffmpeg")
    os.kill(ffmpegProcessId, signal.SIGTERM)
    s.close()

def main():
    me = tello.Tello()
    me.connect()
    me.streamon()
    print(me.get_battery())

    atexit.register(exitRoutine)
    kp.init()

    # 3
    try:
        command = telloCommand
        print(command)

        pro = subprocess.Popen(command,shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        ffmpegProcessId = pro.pid

        print(f"ffmpeg successful  ProcessId {ffmpegProcessId}")

    except:
        print("ffmpeg failed!")
        exit()
    
    cap = cv2.VideoCapture(f"udp://127.0.0.1:{localVideoStreamPort}", cv2.CAP_FFMPEG)

    while True:
        
        vals = getKeyboardIinputNode()

        ret, frame = cap.read()
        height = me.get_height()
        if height > 1200:  #Safety feature to land if height > 8 meters.
            me.land()
            break

        frame = cv2.resize(frame, (w,h))

        cv2.putText(frame, f"Altitude: {height} Searching for {objectToFind if objectToFind else 'No'}",
                        (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 255), 1)

        if informControlCenter:
            cv2.putText(frame, f"Found Vehicle of Interest",
                        (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 0, 200), 2)  
            cv2.putText(frame, f"Alerted Control Center",
                        (20, 120), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 0, 200), 2)  
            cv2.putText(frame, f"Found {objectToFind}",
                        (20, 160), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 0, 200), 2)       
        

        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

        blob = cv2.dnn.blobFromImage(frame, 1 / 255, (whT, whT), [0, 0, 0], 1, crop=False)
        net.setInput(blob)
        layersNames = net.getLayerNames()
        outputNames = [(layersNames[i - 1]) for i in net.getUnconnectedOutLayers()]
        outputs = net.forward(outputNames)
        findObjects(outputs, frame)


        cv2.imshow('video',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            me.land()
            print(me.get_battery())
            break


if (__name__ == "__main__"):
    main()
    