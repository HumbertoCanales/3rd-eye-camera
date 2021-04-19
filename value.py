class Value():
    def __init__(self, temperature, humidity, date_value):
        self.temperature = temperature
        self.humidity = humidity
        self.date_value = date_value

    def getDocument(self):
        document = {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "date_value": self.date_value
        }
        return document
