import requests
import os
from pprint import pprint
import datetime
import uuid
from add import get_ip_address


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
        r = requests.post(url, data=data)
        return r.status_code

    def changeIp(self):
        url = self.api_url + 'repo/cam/ip'
        ip = get_ip_address()
        data = {
            'code': self.code,
            'ip': ip
        }
        r = requests.put(url, data=data)
        return r.status_code

    def startVideo(self):
        url = self.api_url + 'repo/video'
        data = {
            'code': self.code
        }
        r = requests.post(url, data=data)
        return r.status_code

    def saveImage(self, frame, obj_type, distance):
        url = self.api_url + 'repo/img'
        date = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join(["image", date])
        route = filename + str(uuid.uuid4()) + ".jpg"
        data = {
            'route': route,
            'code': self.code,
            'obj_type': obj_type,
            'distance': distance
        }
        files = {
            'image': (route, frame, 'multipart/form-data', {'Expires': '0'})}
        r = requests.post(url, files=files, data=data)
        return r.status_code

    def saveValues(self, temp, hum):
        url = self.api_url + 'repo/values'
        data = {
            'code': self.code,
            'temperature': temp,
            'humidity': hum
        }
        r = requests.post(url, data=data)
        return r.status_code
