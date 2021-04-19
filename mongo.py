from pymongo import MongoClient
from pymongo import errors as mongoerrors
from datetime import datetime as time
from value import Value
from image import Image


class MongoDB:
    def __init__(self):
        self.client = "mongodb://localhost:27017/"
        self.database = "integradora"

    def __connect__(self):
        try:
            self.connect = MongoClient(self.client)
            self.db = self.connect[self.database]
        except mongoerrors.OperationFailure as e:
            print("Could not connect to MongoDB")
            print(e.code)
            print(e.details)

    def verDatos(self, collection, parametro={}):
        self.__connect__()
        c = self.db[collection]
        cursor = c.find()
        return cursor

    def addRegistro(self, collection, obj):
        document = obj.getDocument()
        self.__connect__()
        col = self.db[collection]
        x = col.insert(document)
        return x

    def getValues(self):
        values = self.verDatos("values")
        vals = []
        for value in values:
            val = Value(value['temperature'],
                        value['humidity'], value['date_value'])
            vals.append(val)
        return vals

    def getImages(self):
        images = self.verDatos("images")
        imgs = []
        for image in images:
            img = Image(image['route'], image['date_photo'],
                        image['distance'], image['obj_type'])
            imgs.append(img)
        return imgs

    def dropCollection(self, collection):
        self.__connect__()
        c = self.db[collection]
        c.drop()

    """def addSensor(self, colection, sensor):
        self.addRegistro(colection, sensor)

    def getSensores(self):
        try:
            sensores = self.verDatos("mis_sensores")
            logs = []
            for sensor in sensores:
                sensor = Sensor(sensor['nombre'],
                                sensor['tipo'], sensor['pines'])
                logs.append(sensor)
            return logs
        except:
            return None"""
