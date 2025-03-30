import json
from uuid import UUID
from datetime import datetime, date


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def serialize_to_json(obj):
    """
    Serializa um objeto para JSON usando o UUIDEncoder customizado.
    """
    return json.dumps(obj, cls=UUIDEncoder)
