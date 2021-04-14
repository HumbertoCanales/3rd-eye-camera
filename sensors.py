import Adafruit_DHT as adafruit_dht
import RPi.GPIO as GPIO
import datetime as d
import time
# from Sensor import Sensor
# from Registro import Registro


class Sensors():
    def __init__(self):
        self.arreglo = []
        GPIO.setmode(GPIO.BCM)
        self.PIN_TRIG = 23
        self.PIN_ECHO = 24
        self.PIN_PIR = 26
        self.PIN_DHT = 21
        self.PIN_LIGHT = 16

        GPIO.setup(self.PIN_LIGHT, GPIO.IN)
        GPIO.setup(self.PIN_PIR, GPIO.IN)
        GPIO.setup(self.PIN_TRIG, GPIO.OUT)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)

    def getTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def getPIR(self):
        value = GPIO.input(self.PIN_PIR)
        return value

    def getLight(self):
        value = GPIO.input(self.PIN_LIGHT)
        return value

    def getDistance(self):
        try:
            GPIO.output(self.PIN_TRIG, True)
            time.sleep(0.00001)
            GPIO.output(self.PIN_TRIG, False)
            while GPIO.input(self.PIN_ECHO) == 0:
                start = time.time()
            while GPIO.input(self.PIN_ECHO) == 1:
                end = time.time()
            time.sleep(0.01)
            duration = end - start
            distance = (34300 * duration) / 2
            return round(distance, 2)
        except RuntimeError as error:
            print("Error: " + error)

    def getTempHum(self):
        i = 0
        while i <= 5:
            i += 1
            try:
                humedad, temperatura = adafruit_dht.read(11, self.PIN_DHT)
                if humedad is not None and temperatura is not None:
                    return humedad, temperatura
                    break
            except RuntimeError as error:
                print("Error: " + error)

    def getValores(self):
        dht = sen.getTempHum()
        values = {
            'humidity': dht[0],
            'temperature': dht[1]
        }
        return values
