import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
from flask_cors import CORS
import time
import threading
import requests
import os
from pprint import pprint
import datetime
import uuid
from add import get_ip_address
from sensors import Sensors
from http_module import Http

photo_interval = 15
values_interval = 60

video_camera = VideoCamera(flip=True)
object_classifier = cv2.CascadeClassifier(
    "models/facial_recognition_model.xml")  # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['BASIC_AUTH_USERNAME'] = ''
app.config['BASIC_AUTH_PASSWORD'] = ''
app.config['BASIC_AUTH_FORCE'] = False

basic_auth = BasicAuth(app)
last_found = 0
last_pres = 0
last_values = 0

api_url = 'http://192.168.80.128:3333/v1/api/'
default_name = 'SECURITY CAMERA'
code = '123456'

sensors = Sensors()
http = Http(api_url, default_name, code)


def check_for_objects():
    global last_found
    global last_pres
    global last_values
    try:
        status = http.register()
        if status == 500:
            print("Server error")
        elif status == 422:
            print("Camera already registered")
            try:
                http.changeIp()
                print("Ip address updated")
            except:
                print("Error changing camera ip address: ", sys.exc_info()[0])
        elif status == 201:
            print("Camera registered succesfully!")
    except:
        print("Error registering camera: ", sys.exc_info()[0])
        return
    try:
        status = http.startVideo()
        if status == 500:
            print("Server error")
        elif status == 200:
            print("Video iniciado")
    except:
        print("Error starting video: ", sys.exc_info()[0])
        return

    while True:
        frame, found_obj = video_camera.get_object(object_classifier)
        presence = sensors.getPIR()
        if found_obj and (time.time() - last_found) > photo_interval:
            try:
                distance = sensors.getDistance()
                http.saveImage(frame, 1, distance)
                print("Person image saved!")
            except:
                print("Error sending image: ", sys.exc_info()[0])
            last_found = time.time()
        elif presence and (time.time() - last_pres) > photo_interval:
            try:
                distance = sensors.getDistance()
                http.saveImage(frame, 2, distance)
                print("Presence image saved!")
            except:
                print("Error sending image: ", sys.exc_info()[0])
            last_pres = time.time()
        if (time.time() - last_values) > values_interval:
            try:
                dht = sensors.getTempHum()
                http.saveValues(dht[0], dht[1])
                print("Values saved!")
            except:
                print("Error saving image: ", sys.exc_info()[0])
            last_values = time.time()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    resp = Response()
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
    return resp


def gen(camera):
    while True:
        frame, found_obj = video_camera.get_object(object_classifier)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='192.168.80.117', debug=False)
