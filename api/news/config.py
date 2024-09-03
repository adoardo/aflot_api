import json
from datetime import date


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
