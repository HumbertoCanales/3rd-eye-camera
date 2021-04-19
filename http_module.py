import requests
import os
from pprint import pprint
import datetime
import uuid
from add import get_ip_address
import cv2
from PIL import Image


class Http():
    def __init__(self, api_url, default_name, code):
        self.api_url = api_url
        self.default_name = default_name
        self.code = code

    def register(self):
        url = self.api_url + 'repo/cam'
        ip = get_ip_address()
        data = {
            'code': self.code,
            'name': self.default_name,
            'ip': ip
        }
        r = requests.post(url, data=data, timeout=2.5)
        return r.status_code

    def changeIp(self):
        url = self.api_url + 'repo/cam/ip'
        ip = get_ip_address()
        data = {
            'code': self.code,
            'ip': ip
        }
        r = requests.put(url, data=data, timeout=2.5)
        return r.status_code

    def startVideo(self):
        url = self.api_url + 'repo/video'
        data = {
            'code': self.code
        }
        r = requests.post(url, data=data, timeout=2.5)
        return r.status_code

    def saveImage(self, frame, obj_type, distance, route):
        url = self.api_url + 'repo/img'
        data = {
            'route': route,
            'code': self.code,
            'obj_type': obj_type,
            'distance': distance
        }
        files = {
            'image': (route, frame, 'multipart/form-data', {'Expires': '0'})}
        r = requests.post(url, files=files, data=data, timeout=2.5)
        return r.status_code

    def saveValues(self, temp, hum):
        url = self.api_url + 'repo/values'
        data = {
            'code': self.code,
            'temperature': temp,
            'humidity': hum
        }
        r = requests.post(url, data=data, timeout=2.5)
        return r.status_code

    def mongoValues(self, values):
        for value in values:
            url = self.api_url + 'repo/values'
            data = {
                'code': self.code,
                'temperature': value.temperature,
                'humidity': value.humidity,
                'date_value': value.date_value
            }
            requests.post(url, data=data, timeout=1.5)

    def mongoImages(self, images):
        for image in images:
            url = self.api_url + 'repo/img'
            data = {
                'route': image.route,
                'code': self.code,
                'obj_type': image.obj_type,
                'distance': image.distance,
                'date_photo': image.date_photo
            }
            path = 'images/' + image.route
            #frame = cv2.imread(path)
            #cv2.imshow('image', frame)
            #im = Image.open(path)
            img = open(path, 'rb').read()
            files = {
                'image': (image.route, img, 'multipart/form-data', {'Expires': '0'})}
            r = requests.post(url, files=files, data=data, timeout=2.5)
            os.remove(path)


"""route = 'image_210419_000940b6a758b5-4d2a-4eb9-b903-09c844183ce6.jpg'
path = r'images/' + route
im = Image.open(path)
print(im)"""
