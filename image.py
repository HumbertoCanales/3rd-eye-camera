class Image():
    def __init__(self, route, date_photo, distance, obj_type):
        self.route = route
        self.date_photo = date_photo
        self.distance = distance
        self.obj_type = obj_type

    def getDocument(self):
        document = {
            "route": self.route,
            "date_photo": self.date_photo,
            "distance": self.distance,
            "obj_type": self.obj_type
        }
        return document
