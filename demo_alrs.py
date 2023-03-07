import numpy as np
import cv2
from cv2 import aruco
from time import sleep
import atexit
from djitellopy import tello

import keyPressModule as kp
import serial
import time

from utils_alrs import distance, drawMarker, drawQuadrant, \
                        getQuadrantInfo, getDirection, \
                        getKeyboardIinputALRS, triggerALRS

isLanding = False
isOpen = False

w, h = 1000, 680
land = False


def exitRoutine():
    print("Killing all process")
    triggerALRS("close")

def main():
    kp.init()

    me = tello.Tello()
    me.connect()
    me.streamon()
    print(me.get_battery())

    atexit.register(exitRoutine)

    while True:
        
        vals = getKeyboardIinputALRS()

        frame = me.get_frame_read().frame
        height = me.get_height()
        if height > 1000:  #Safety feature to land if height > 8 meters.
            me.land()
            break

        frame = cv2.resize(frame, (w,h))

        cv2.putText(frame, f"Altitude: {height} isLanding: {isLanding} Land: {land} Mode: {'Landing'}",
                        (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 255), 1)  
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        
        if land:
            centerX, centerY = w//2, h//2  #Get center of Frame

            drawQuadrant()

            #Find aruCo marker in frame
            aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
            parameters =  aruco.DetectorParameters_create()
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            
            # print(corners)
            if len(corners) > 0:   #if All 4 corners of marker is detected

                ids = ids.flatten()
                markerInfo = drawMarker(corners, ids)  

                cX, cY = markerInfo[0]   #Get marker midpoint

                #Calculate error i.e Distance btw aruco midpoint and frame midpoint
                error = int(distance((cX, cY), (centerX, centerY)))
                markerWidth, markerHeight = markerInfo[1]


                rW, rH = round(markerWidth/w, 1), round(markerHeight/h, 1)    #Calculate ratio
                # rW, rH = 0.4, 0.4
                #Draw line between center of frame and center of marker
                cv2.line(frame, (cX, cY), (centerX,centerY), (254, 255, 0), 3)

                region, delXandY = getQuadrantInfo(cX, cY, centerX, centerY)   #Get the quadrant/region where marker is in and ΔX and ΔY
                delX, delY = delXandY
                delX, delY = int(rW * delX), int(rH * delY)  #Multiple error with ratio

                speedX, speedY = int(np.clip(delX, -100, 100)), int(np.clip(delY, -100, 100))   #front/back and left/right command to send to drone.
                speedX, speedY = getDirection(speedX,speedY,region) if not None else (0,0)    #Add direction to command

                cv2.putText(frame, f"X: {speedX}  Y: {speedY}  Error: {error} Alt: {height}  isLanding: {isLanding}",
                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

                if not isLanding:
                    me.send_rc_control(speedX, speedY, 0, 0)

                if height < 60: #Close enought to the ground
                    me.land()
                    triggerALRS("close")
                    print(me.get_battery())
                
                if error < 25 or isLanding:
                    if not isOpen:
                        isOpen = True
                        triggerALRS("open")
                    if not isLanding:
                        isLanding = True
                    me.send_rc_control(0, 0, -15, 0)
                    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
                
            else:
                print("No marker.........................")
                # isLanding = False
                me.send_rc_control(0, 0, 0, 0) #Stay put
                me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        else:
            me.send_rc_control(vals[0], vals[1], vals[2], vals[3])


        cv2.imshow('video',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            me.land()
            triggerALRS("close")
            print(me.get_battery())
            break


    

if (__name__ == "__main__"):
    main()
    