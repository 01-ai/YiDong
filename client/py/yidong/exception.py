import json


class YDError(Exception):
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data

    def __str__(self) -> str:
        return json.dumps({"code": self.code, "message": self.message})
