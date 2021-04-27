#!/usr/bin/python3

import cv2
import sys
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_cors import CORS
import time
import threading
import requests
import os
import datetime
import uuid
import picamera as pic
from add import get_ip_address
from sensors import Sensors
from http_module import Http
from mongo import MongoDB
from value import Value
from image import Image

photo_interval = 15
values_interval = 120

video_camera = VideoCamera(flip=True)
object_classifier = cv2.CascadeClassifier(
    "/home/pi/Desktop/Integradora/Camera/models/facial_recognition_model.xml")

# App Globals (do not edit)
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

last_found = 0
last_pres = 0
last_values = 0

api_url = 'http://23.21.161.238/v1/api/'
default_name = 'SECURITY CAMERA'
code = 'HOLAPROFES'  # 'L12UL74M44J7418'

sensors = Sensors()
http = Http(api_url, default_name, code)
db = MongoDB()


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

    try:
        status = http.startVideo()
        if status == 500:
            print("Server error")
        elif status == 200 or status == 404:
            print("Video started")
            try:
                values = db.getValues()
                http.mongoValues(values)
                images = db.getImages()
                http.mongoImages(images)
                db.dropCollection('values')
                db.dropCollection('images')
                print("Internal values transfered")
            except:
                print("Error saving mongo values: ", sys.exc_info()[0])
    except:
        print("Error starting video: ", sys.exc_info()[0])

    while True:
        frame, found_obj = video_camera.get_object(object_classifier)
        presence = sensors.getPIR()
        if found_obj and (time.time() - last_found) > photo_interval:
            date = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            filename = "_".join(["image", date])
            route = filename + str(uuid.uuid4()) + ".jpg"
            distance = sensors.getDistance()
            try:
                http.saveImage(frame, 1, distance, route)
                print("Person image saved!")
            except:
                print("Error sending image, now saving locally: ",
                      sys.exc_info()[0])
                video_camera.save_frame(route)
                image = Image(route, datetime.datetime.now(
                ).astimezone().isoformat(), distance, 1)
                db.addRegistro("images", image)
            last_found = time.time()
        elif presence and (time.time() - last_pres) > photo_interval:
            date = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            filename = "_".join(["image", date])
            route = filename + str(uuid.uuid4()) + ".jpg"
            distance = sensors.getDistance()
            try:
                http.saveImage(frame, 2, distance, route)
                print("Presence image saved!")
            except:
                print("Error sending image, now saving locally: ",
                      sys.exc_info()[0])
                video_camera.save_frame(route)
                image = Image(route, datetime.datetime.now(
                ).astimezone().isoformat(), distance, 2)
                db.addRegistro("images", image)
            last_pres = time.time()
        if (time.time() - last_values) > values_interval:
            try:
                dht = sensors.getTempHum()
                value = Value(dht[1], dht[0],
                              datetime.datetime.now().astimezone().isoformat())
                try:
                    http.saveValues(value.temperature, value.humidity)
                    print("Values saved!")
                except:
                    print("Error saving values in server, now saving locally",
                          sys.exc_info()[0])
                    db.addRegistro("values", value)
            except:
                print("DHT sensor connection error", sys.exc_info()[0])

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
        #frame, found_obj = video_camera.get_object(object_classifier)
        frame = camera.get_frame()
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
    app.run(host='127.0.0.1', debug=False)
