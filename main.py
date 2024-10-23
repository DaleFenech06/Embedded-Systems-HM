import cv2
import os
import datetime
import subprocess
from time import sleep
import RPi.GPIO as GPIO
from flask import Flask, redirect, url_for, render_template
from gpiozero import LightSensor
from send_email import attachVideo

#   Variables

led = 21 #  Pin 40
switch = 20 #   Pin 38
buzzer = 26 #   Pin 37
resistor = 4 #  Pin 7

face_cascade = cv2.CascadeClassifier("/home/dale4e/Python/Home Assignment/haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("/home/dale4e/Python/Home Assignment/haarcascade_eye_tree_eyeglasses.xml")
defaultFile = "/home/dale4e/Python/Home Assignment/Videos/Video"
saveFile = defaultFile

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fourcc = cv2.VideoWriter_fourcc(*'H264')

app = Flask(__name__)

@app.route("/")

#   Functions

def home():

    dt = getRecentVideoDate()
    lt = getLightLevel()
    vd = getVideoLength()
    
    return render_template("index.html", date=dt, light=lt, length=vd)

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(led, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(switch, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def setupVideo():
    global out
    global saveFile
    index = 1
    if(os.path.exists(defaultFile + ".mp4") == True):
        while (os.path.exists(saveFile + ".mp4" ) == True):
            saveFile = defaultFile + str(index)
            index += 1
    out = cv2.VideoWriter(saveFile + '.mp4',fourcc, 8.0, (int(w),int(h)))
    
def detectFace():
    ret, frame = cap.read()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame_gray, 1.25, 4)
    eyes = eye_cascade.detectMultiScale(frame_gray)
    GPIO.output(led,0)
    GPIO.output(buzzer,0) 
    
    for(x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0),2)
        rec_gray = frame_gray[y:y+h, x:x+w]
        rec_color = frame[y:y+h, x:x+w]
        GPIO.output(buzzer,1)
        GPIO.output(led,1) 

    for(ex,ey,ew,eh) in eyes:
        cv2.rectangle(frame,(ex,ey),(ex+ew,ey+eh),(0,255,255),2)
        GPIO.output(buzzer,1)
        GPIO.output(led,1)

    if ret == False:
        print("Can't see.")
    else:
        out.write(frame)
        cv2.imshow('Video Capture', frame)
            
    key = cv2.waitKey(1)

def getLightLevel():
    ldr = LightSensor(resistor)
    lighting = ""
    if(ldr.value*100 >= 80):
        lighting = "Very bright light"
    if(ldr.value*100 >= 70 and ldr.value*100 < 80):
        lighting = "Bright light"
    elif(ldr.value*100 >= 40 and ldr.value*100 < 70):
        lighting = "Medium light"
    elif(ldr.value*100 >= 10 and ldr.value*100 < 40):
        lighting = "Dim light"
    elif(ldr.value*100 < 10):
        lighting = "No light"
    return lighting    

def getRecentVideoDate():
    global saveFile
    recentVideo = os.path.getctime(saveFile + ".mp4")
    dateAndtime = datetime.datetime.fromtimestamp(recentVideo).date()
    return dateAndtime

def getVideoLength():
    global saveFile
    video = cv2.VideoCapture(saveFile + ".mp4")

    frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)

    seconds = round(frames/fps)
    video_time = datetime.timedelta(seconds=seconds)
    return video_time

def closeVideo():
    print("Ending recording...")
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def closeGPIO():
    print("Exiting GPIO ports..")
    GPIO.output(led,0)
    GPIO.output(buzzer,0)
    GPIO.cleanup()

#   Main Code
    
try:
    setupGPIO()
    setupVideo()
    print("Press button to stop recording.")
    while True:
        if GPIO.input(switch) == True:
            detectFace()
        else:
            closeVideo()
            closeGPIO()
            attachVideo(saveFile + '.mp4')
            break
    if __name__ == "__main__":
        print("Loading website...")
        app.run(host='192.168.0.10', port=5000)
except KeyboardInterrupt:
    closeVideo()
    closeGPIO()
    if __name__ == "__main__":
        print("Loading website...")
        app.run(host='192.168.0.10', port=5000)
