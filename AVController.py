# importing libraries
import cv2
import numpy as np
from threading import Thread
from playsound import playsound
import time
import sys

file = ''

window_width = 550
window_height = 650

def playFile(inputFile, audio=True):
    global file
    file = inputFile
    # Create a VideoCapture object and read from input file
    cap = cv2.VideoCapture(file)

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video file")

    # Check to play audio
    if audio == True:
        Thread(target = audioEngine).start()

  # Read until video is completed
    while(cap.isOpened()):

    # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:

            # Display the resulting frame

            #cv2.WINDOW_NORMAL makes the output window resizealbe
            cv2.namedWindow('Resized Window', cv2.WINDOW_NORMAL)
            #resize the window according to the screen resolution
            cv2.resizeWindow('Resized Window', window_width, window_height)

            cv2.imshow('Resized Window', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

      # Break the loop
        else:
            break

    # When everything done, release
    # the video capture object
    cap.release()

def close():
    # Closes all the frames
    cv2.destroyAllWindows()

def audioEngine():
    time.sleep(.4)
    playsound(file)

def audioHeadless(fileInput):
    playsound(fileInput)
