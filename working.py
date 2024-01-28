import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume




wCam, hCam = 1280, 720


cap = cv2.VideoCapture(0)

pTime = 0


detector = htm.handDetector(detectionCon=0.7, maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (0, 0, 0)
delay = 10

current_time = time.time()
closing_time = current_time+delay

while True:
    success, img = cap.read()
   
    img,hand_found= detector.findHands(img)
    current_time = time.time()
    if not hand_found:
        cv2.putText(img,"No hand detected,terminating in 10 seconds",(30,100),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),1)
        if current_time >= closing_time:
            
            break
    else:
        closing_time = current_time+delay



   
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:
            #filter according to size
            #area of bbox
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
            
            if 250 < area < 1000:

            # Find Distance between index and Thumb
                length, img, lineInfo = detector.findDistance(4, 8, img)
                fingers = detector.fingersUp()
                
                if  not fingers[0]:
                    cv2.putText(img,"Hand gesture not appropriate",(50,100),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,0),1)
                    
                else:
                # Convert Volume
                    volBar = np.interp(length, [50, 200], [400, 150])
                    volPer = np.interp(length, [50, 200], [0, 100])

                # Reduce Resolution to make it smoother
                    smoothness = 10
                    volPer = smoothness * round(volPer / smoothness)

                # Check fingers up
                    #fingers = detector.fingersUp()
                    #gesture_detected = detector.gestures()
                    # print(fingers)

                # set volume
                    if not fingers[4]:
                        volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 0, 255), cv2.FILLED)
                        colorVol = (255, 0, 0)
                    else:
                        colorVol = (0, 0, 0)
                # terminate if rock on sign is detected
                    if not fingers[2] and not fingers[3]:
                        break


        

    # Drawings
    cv2.rectangle(img, (50, 150), (75, 400), (0, 0, 0), 2)
    cv2.rectangle(img, (50, int(volBar)), (75, 400), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (0, 0, 0), 1)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, colorVol, 2)

    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 30), cv2.FONT_HERSHEY_COMPLEX,
                1, (0, 0, 0), 1)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xff == ord('.'): 
        break